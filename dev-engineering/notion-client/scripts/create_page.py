#!/usr/bin/env python3
"""
Notion 页面创建脚本
用法: python create_page.py --database-id <id> --title <title> [options]
"""

import os
import sys
import argparse
import json
from typing import Optional, List, Dict, Any

try:
    from notion_client import Client, APIResponseError
except ImportError:
    print("Error: notion-client not installed. Run: pip install notion-client --break-system-packages")
    sys.exit(1)


def create_rich_text(content: str) -> List[Dict[str, Any]]:
    """创建 rich_text 数组"""
    return [{"type": "text", "text": {"content": content}}]


def create_page_in_database(
    notion: Client,
    database_id: str,
    title: str,
    properties: Optional[Dict[str, Any]] = None,
    content: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    在数据库中创建页面
    
    Args:
        notion: Notion 客户端
        database_id: 数据库 ID
        title: 页面标题
        properties: 额外属性 (可选)
        content: 页面内容段落列表 (可选)
    
    Returns:
        创建的页面对象
    """
    # 构建属性
    page_properties = {
        "Name": {"title": create_rich_text(title)}  # 假设标题属性名为 Name
    }
    
    # 尝试使用 title 作为属性名（如果 Name 不存在）
    # 合并额外属性
    if properties:
        page_properties.update(properties)
    
    # 构建子块
    children = []
    if content:
        for paragraph in content:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": create_rich_text(paragraph)
                }
            })
    
    # 创建页面
    create_params = {
        "parent": {"database_id": database_id},
        "properties": page_properties
    }
    
    if children:
        create_params["children"] = children
    
    return notion.pages.create(**create_params)


def create_page_in_page(
    notion: Client,
    parent_page_id: str,
    title: str,
    content: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    在页面下创建子页面
    
    Args:
        notion: Notion 客户端
        parent_page_id: 父页面 ID
        title: 页面标题
        content: 页面内容段落列表 (可选)
    
    Returns:
        创建的页面对象
    """
    children = []
    if content:
        for paragraph in content:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": create_rich_text(paragraph)
                }
            })
    
    create_params = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": {"title": create_rich_text(title)}
        }
    }
    
    if children:
        create_params["children"] = children
    
    return notion.pages.create(**create_params)


def main():
    parser = argparse.ArgumentParser(description="创建 Notion 页面")
    parser.add_argument("--database-id", "-d", help="目标数据库 ID")
    parser.add_argument("--page-id", "-p", help="父页面 ID (创建子页面)")
    parser.add_argument("--title", "-t", required=True, help="页面标题")
    parser.add_argument("--content", "-c", nargs="*", help="页面内容段落")
    parser.add_argument("--properties", help="额外属性 (JSON 格式)")
    parser.add_argument("--token", help="Notion API Token (默认使用 NOTION_TOKEN 环境变量)")
    
    args = parser.parse_args()
    
    # 验证参数
    if not args.database_id and not args.page_id:
        print("Error: 必须指定 --database-id 或 --page-id")
        sys.exit(1)
    
    # 获取 Token
    token = args.token or os.environ.get("NOTION_TOKEN")
    if not token:
        print("Error: 需要 NOTION_TOKEN 环境变量或 --token 参数")
        sys.exit(1)
    
    # 初始化客户端
    notion = Client(auth=token)
    
    # 解析额外属性
    extra_properties = None
    if args.properties:
        try:
            extra_properties = json.loads(args.properties)
        except json.JSONDecodeError:
            print("Error: 属性格式无效，需要 JSON 格式")
            sys.exit(1)
    
    try:
        if args.database_id:
            page = create_page_in_database(
                notion,
                args.database_id,
                args.title,
                extra_properties,
                args.content
            )
        else:
            page = create_page_in_page(
                notion,
                args.page_id,
                args.title,
                args.content
            )
        
        print(f"✓ 页面创建成功")
        print(f"  ID: {page['id']}")
        print(f"  URL: {page['url']}")
        
    except APIResponseError as e:
        print(f"Error: {e.code} - {e.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
