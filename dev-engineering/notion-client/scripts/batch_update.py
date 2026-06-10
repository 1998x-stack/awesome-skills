#!/usr/bin/env python3
"""
Notion 批量更新脚本
用法: python batch_update.py --database-id <id> --filter <filter> --update <properties>
"""

import os
import sys
import argparse
import json
import time
from typing import Optional, Dict, Any, List

try:
    from notion_client import Client, APIResponseError
except ImportError:
    print("Error: notion-client not installed. Run: pip install notion-client --break-system-packages")
    sys.exit(1)


def query_all_pages(
    notion: Client,
    database_id: str,
    filter_obj: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """获取数据库所有匹配的页面"""
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
    
    return all_results


def batch_update_pages(
    notion: Client,
    pages: List[Dict[str, Any]],
    update_properties: Dict[str, Any],
    dry_run: bool = False,
    delay: float = 0.3
) -> tuple:
    """
    批量更新页面
    
    Args:
        notion: Notion 客户端
        pages: 要更新的页面列表
        update_properties: 要更新的属性
        dry_run: 是否为演练模式（不实际更新）
        delay: 每次更新之间的延迟（秒）
    
    Returns:
        (成功数, 失败数)
    """
    success_count = 0
    fail_count = 0
    
    for i, page in enumerate(pages, 1):
        page_id = page["id"]
        
        # 提取标题用于显示
        title = "(unknown)"
        for prop_name, prop_value in page["properties"].items():
            if prop_value.get("type") == "title" and prop_value.get("title"):
                title = prop_value["title"][0]["text"]["content"]
                break
        
        if dry_run:
            print(f"[{i}/{len(pages)}] 将更新: {title} ({page_id})")
            success_count += 1
        else:
            try:
                notion.pages.update(
                    page_id=page_id,
                    properties=update_properties
                )
                print(f"[{i}/{len(pages)}] ✓ 已更新: {title}")
                success_count += 1
                
                # 延迟以避免频率限制
                if delay > 0 and i < len(pages):
                    time.sleep(delay)
                    
            except APIResponseError as e:
                print(f"[{i}/{len(pages)}] ✗ 更新失败: {title} - {e.message}")
                fail_count += 1
    
    return success_count, fail_count


def batch_archive_pages(
    notion: Client,
    pages: List[Dict[str, Any]],
    dry_run: bool = False,
    delay: float = 0.3
) -> tuple:
    """批量归档页面"""
    return batch_update_pages(
        notion, pages, {"archived": True}, dry_run, delay
    )


def main():
    parser = argparse.ArgumentParser(description="批量更新 Notion 页面")
    parser.add_argument("--database-id", "-d", required=True, help="数据库 ID")
    parser.add_argument("--filter", "-f", help="过滤条件 (JSON 格式)")
    parser.add_argument("--update", "-u", help="要更新的属性 (JSON 格式)")
    parser.add_argument("--archive", action="store_true", help="归档匹配的页面")
    parser.add_argument("--dry-run", action="store_true", help="演练模式（不实际更新）")
    parser.add_argument("--delay", type=float, default=0.3, help="更新间隔（秒）")
    parser.add_argument("--token", help="Notion API Token")
    parser.add_argument("--yes", "-y", action="store_true", help="跳过确认")
    
    args = parser.parse_args()
    
    # 验证参数
    if not args.update and not args.archive:
        print("Error: 必须指定 --update 或 --archive")
        sys.exit(1)
    
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
    
    # 解析更新属性
    update_properties = None
    if args.update:
        try:
            update_properties = json.loads(args.update)
        except json.JSONDecodeError:
            print("Error: 更新属性格式无效")
            sys.exit(1)
    
    try:
        # 获取匹配的页面
        print("正在查询数据库...")
        pages = query_all_pages(notion, args.database_id, filter_obj)
        
        if not pages:
            print("没有匹配的页面")
            return
        
        print(f"找到 {len(pages)} 个匹配的页面")
        
        # 确认操作
        if not args.yes and not args.dry_run:
            action = "归档" if args.archive else "更新"
            confirm = input(f"确定要{action}这些页面吗？(y/N): ")
            if confirm.lower() != "y":
                print("已取消")
                return
        
        # 执行批量操作
        if args.archive:
            success, fail = batch_archive_pages(
                notion, pages, args.dry_run, args.delay
            )
        else:
            success, fail = batch_update_pages(
                notion, pages, update_properties, args.dry_run, args.delay
            )
        
        # 输出结果
        print(f"\n完成: {success} 成功, {fail} 失败")
        if args.dry_run:
            print("(演练模式，未实际更新)")
        
    except APIResponseError as e:
        print(f"Error: {e.code} - {e.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
