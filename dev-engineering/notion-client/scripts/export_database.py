#!/usr/bin/env python3
"""
Notion 数据库导出脚本
用法: python export_database.py --database-id <id> --output <file> [options]
"""

import os
import sys
import argparse
import json
import csv
from typing import Optional, Dict, Any, List

try:
    from notion_client import Client, APIResponseError
except ImportError:
    print("Error: notion-client not installed. Run: pip install notion-client --break-system-packages")
    sys.exit(1)


def extract_property_value(prop: Dict[str, Any], for_csv: bool = False) -> Any:
    """
    提取属性值
    
    Args:
        prop: 属性对象
        for_csv: 是否为 CSV 格式（数组转字符串）
    """
    prop_type = prop.get("type")
    
    if prop_type == "title":
        return prop["title"][0]["text"]["content"] if prop["title"] else ""
    elif prop_type == "rich_text":
        return "".join([rt["text"]["content"] for rt in prop["rich_text"]])
    elif prop_type == "number":
        return prop["number"]
    elif prop_type == "select":
        return prop["select"]["name"] if prop["select"] else None
    elif prop_type == "multi_select":
        values = [item["name"] for item in prop["multi_select"]]
        return ", ".join(values) if for_csv else values
    elif prop_type == "date":
        if prop["date"]:
            result = prop["date"]["start"]
            if prop["date"].get("end"):
                result += " → " + prop["date"]["end"]
            return result
        return None
    elif prop_type == "checkbox":
        return prop["checkbox"]
    elif prop_type == "url":
        return prop["url"]
    elif prop_type == "email":
        return prop["email"]
    elif prop_type == "phone_number":
        return prop["phone_number"]
    elif prop_type == "people":
        values = [p.get("name", p["id"]) for p in prop["people"]]
        return ", ".join(values) if for_csv else values
    elif prop_type == "relation":
        values = [r["id"] for r in prop["relation"]]
        return ", ".join(values) if for_csv else values
    elif prop_type == "status":
        return prop["status"]["name"] if prop["status"] else None
    elif prop_type == "formula":
        formula = prop["formula"]
        return formula.get(formula["type"])
    elif prop_type in ["created_time", "last_edited_time"]:
        return prop[prop_type]
    elif prop_type in ["created_by", "last_edited_by"]:
        user = prop[prop_type]
        return user.get("name", user["id"])
    elif prop_type == "files":
        files = prop["files"]
        urls = []
        for f in files:
            if f["type"] == "external":
                urls.append(f["external"]["url"])
            elif f["type"] == "file":
                urls.append(f["file"]["url"])
        return ", ".join(urls) if for_csv else urls
    elif prop_type == "rollup":
        rollup = prop["rollup"]
        if rollup["type"] == "array":
            return str(len(rollup.get("array", []))) + " items"
        return rollup.get(rollup["type"])
    else:
        return None


def query_all_pages(
    notion: Client,
    database_id: str,
    filter_obj: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """获取数据库所有页面"""
    all_results = []
    start_cursor = None
    
    while True:
        query_params = {
            "data_source_id": database_id,
            "page_size": 100
        }
        
        if filter_obj:
            query_params["filter"] = filter_obj
        if start_cursor:
            query_params["start_cursor"] = start_cursor
        
        response = notion.data_sources.query(**query_params)
        all_results.extend(response["results"])
        
        if not response["has_more"]:
            break
        
        start_cursor = response["next_cursor"]
        print(f"  已获取 {len(all_results)} 条记录...")
    
    return all_results


def export_to_json(
    pages: List[Dict[str, Any]],
    output_file: str,
    include_id: bool = True,
    include_url: bool = True
) -> None:
    """导出为 JSON"""
    export_data = []
    
    for page in pages:
        item = {}
        
        if include_id:
            item["id"] = page["id"]
        if include_url:
            item["url"] = page["url"]
        
        item["created_time"] = page["created_time"]
        item["last_edited_time"] = page["last_edited_time"]
        
        for prop_name, prop_value in page["properties"].items():
            item[prop_name] = extract_property_value(prop_value, for_csv=False)
        
        export_data.append(item)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)


def export_to_csv(
    pages: List[Dict[str, Any]],
    output_file: str,
    include_id: bool = True,
    include_url: bool = True
) -> None:
    """导出为 CSV"""
    if not pages:
        return
    
    # 确定列名
    columns = []
    if include_id:
        columns.append("id")
    if include_url:
        columns.append("url")
    columns.append("created_time")
    columns.append("last_edited_time")
    
    # 添加属性列
    prop_names = list(pages[0]["properties"].keys())
    columns.extend(prop_names)
    
    # 写入 CSV
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        
        for page in pages:
            row = {}
            
            if include_id:
                row["id"] = page["id"]
            if include_url:
                row["url"] = page["url"]
            
            row["created_time"] = page["created_time"]
            row["last_edited_time"] = page["last_edited_time"]
            
            for prop_name in prop_names:
                if prop_name in page["properties"]:
                    value = extract_property_value(page["properties"][prop_name], for_csv=True)
                    row[prop_name] = value if value is not None else ""
                else:
                    row[prop_name] = ""
            
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="导出 Notion 数据库")
    parser.add_argument("--database-id", "-d", required=True, help="数据库 ID")
    parser.add_argument("--output", "-o", required=True, help="输出文件路径")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="输出格式")
    parser.add_argument("--filter", "-f", help="过滤条件 (JSON 格式)")
    parser.add_argument("--no-id", action="store_true", help="不包含 ID 列")
    parser.add_argument("--no-url", action="store_true", help="不包含 URL 列")
    parser.add_argument("--token", help="Notion API Token")
    
    args = parser.parse_args()
    
    # 获取 Token
    token = args.token or os.environ.get("NOTION_TOKEN")
    if not token:
        print("Error: 需要 NOTION_TOKEN 环境变量或 --token 参数")
        sys.exit(1)
    
    # 初始化客户端
    notion = Client(auth=token)
    
    # 解析过滤条件
    filter_obj = None
    if args.filter:
        try:
            filter_obj = json.loads(args.filter)
        except json.JSONDecodeError:
            print("Error: 过滤条件格式无效")
            sys.exit(1)
    
    try:
        # 获取所有页面
        print("正在获取数据...")
        pages = query_all_pages(notion, args.database_id, filter_obj)
        
        if not pages:
            print("没有数据")
            return
        
        print(f"共 {len(pages)} 条记录")
        
        # 导出
        print(f"正在导出到 {args.output}...")
        
        if args.format == "csv":
            export_to_csv(
                pages, args.output,
                include_id=not args.no_id,
                include_url=not args.no_url
            )
        else:
            export_to_json(
                pages, args.output,
                include_id=not args.no_id,
                include_url=not args.no_url
            )
        
        print(f"✓ 导出完成: {args.output}")
        
    except APIResponseError as e:
        print(f"Error: {e.code} - {e.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
