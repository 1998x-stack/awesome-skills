#!/usr/bin/env python3
"""
Notion 数据库查询脚本
用法: python query_database.py --database-id <id> [options]
"""

import os
import sys
import argparse
import json
from typing import Optional, Dict, Any, List

try:
    from notion_client import Client, APIResponseError
except ImportError:
    print("Error: notion-client not installed. Run: pip install notion-client --break-system-packages")
    sys.exit(1)


def extract_title(properties: Dict[str, Any], title_key: str = "Name") -> str:
    """从页面属性中提取标题"""
    # 尝试常见的标题属性名
    for key in [title_key, "Title", "title", "Name", "name", "Task", "任务", "标题"]:
        if key in properties:
            prop = properties[key]
            if prop.get("type") == "title" and prop.get("title"):
                return prop["title"][0]["text"]["content"]
    return "(无标题)"


def extract_property_value(prop: Dict[str, Any]) -> Any:
    """提取属性值"""
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
        return [item["name"] for item in prop["multi_select"]]
    elif prop_type == "date":
        if prop["date"]:
            return prop["date"]["start"] + (" → " + prop["date"]["end"] if prop["date"].get("end") else "")
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
        return [p.get("name", p["id"]) for p in prop["people"]]
    elif prop_type == "relation":
        return [r["id"] for r in prop["relation"]]
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
    else:
        return f"<{prop_type}>"


def query_database(
    notion: Client,
    database_id: str,
    filter_obj: Optional[Dict[str, Any]] = None,
    sorts: Optional[List[Dict[str, Any]]] = None,
    page_size: int = 100,
    get_all: bool = False
) -> List[Dict[str, Any]]:
    """
    查询数据库
    
    Args:
        notion: Notion 客户端
        database_id: 数据库 ID
        filter_obj: 过滤条件
        sorts: 排序条件
        page_size: 每页数量
        get_all: 是否获取所有结果
    
    Returns:
        页面列表
    """
    all_results = []
    start_cursor = None
    
    while True:
        query_params = {
            "data_source_id": database_id,
            "page_size": page_size
        }
        
        if filter_obj:
            query_params["filter"] = filter_obj
        if sorts:
            query_params["sorts"] = sorts
        if start_cursor:
            query_params["start_cursor"] = start_cursor
        
        response = notion.data_sources.query(**query_params)
        all_results.extend(response["results"])
        
        if not get_all or not response["has_more"]:
            break
        
        start_cursor = response["next_cursor"]
    
    return all_results


def format_results(
    pages: List[Dict[str, Any]],
    output_format: str = "table",
    show_properties: Optional[List[str]] = None
) -> None:
    """格式化输出结果"""
    if not pages:
        print("(无结果)")
        return
    
    if output_format == "json":
        # JSON 输出
        output = []
        for page in pages:
            item = {"id": page["id"], "url": page["url"], "properties": {}}
            for prop_name, prop_value in page["properties"].items():
                item["properties"][prop_name] = extract_property_value(prop_value)
            output.append(item)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        
    elif output_format == "simple":
        # 简单列表
        for i, page in enumerate(pages, 1):
            title = extract_title(page["properties"])
            print(f"{i}. {title}")
            print(f"   ID: {page['id']}")
        
    else:
        # 表格格式
        # 确定要显示的属性
        if show_properties:
            props_to_show = show_properties
        else:
            # 获取所有属性名（从第一个页面）
            props_to_show = list(pages[0]["properties"].keys())[:5]  # 最多显示5列
        
        # 打印表头
        header = "| # | " + " | ".join(props_to_show) + " |"
        separator = "|" + "|".join(["---"] * (len(props_to_show) + 1)) + "|"
        print(header)
        print(separator)
        
        # 打印数据行
        for i, page in enumerate(pages, 1):
            values = []
            for prop_name in props_to_show:
                if prop_name in page["properties"]:
                    value = extract_property_value(page["properties"][prop_name])
                    # 截断过长的值
                    str_value = str(value) if value is not None else ""
                    if len(str_value) > 30:
                        str_value = str_value[:27] + "..."
                    values.append(str_value)
                else:
                    values.append("")
            print(f"| {i} | " + " | ".join(values) + " |")


def main():
    parser = argparse.ArgumentParser(description="查询 Notion 数据库")
    parser.add_argument("--database-id", "-d", required=True, help="数据库 ID")
    parser.add_argument("--filter", "-f", help="过滤条件 (JSON 格式)")
    parser.add_argument("--sort", "-s", help="排序条件 (JSON 格式)")
    parser.add_argument("--limit", "-l", type=int, default=100, help="结果数量限制")
    parser.add_argument("--all", "-a", action="store_true", help="获取所有结果")
    parser.add_argument("--format", choices=["table", "json", "simple"], default="table", help="输出格式")
    parser.add_argument("--properties", "-p", nargs="*", help="要显示的属性名")
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
    
    # 解析排序条件
    sorts = None
    if args.sort:
        try:
            sorts = json.loads(args.sort)
            if not isinstance(sorts, list):
                sorts = [sorts]
        except json.JSONDecodeError:
            print("Error: 排序条件格式无效")
            sys.exit(1)
    
    try:
        pages = query_database(
            notion,
            args.database_id,
            filter_obj,
            sorts,
            args.limit,
            args.all
        )
        
        print(f"共 {len(pages)} 条结果\n")
        format_results(pages, args.format, args.properties)
        
    except APIResponseError as e:
        print(f"Error: {e.code} - {e.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
