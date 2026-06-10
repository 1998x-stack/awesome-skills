---
name: notion-client
description: |
  Python Notion API 客户端集成，支持完整的 Notion 工作区操作。
  用于: (1) 创建、更新、删除页面和数据库,
  (2) 查询数据库并过滤/排序结果,
  (3) 管理块内容（段落、标题、列表、代码块等）,
  (4) 搜索工作区内容,
  (5) 用户和评论操作,
  (6) 文件上传。
  当用户需要与 Notion API 交互、自动化 Notion 工作流、
  同步数据到 Notion、或从 Notion 提取数据时触发。
---

# Notion Client Skill

Python Notion API 客户端集成，基于 `notion-client` 库（notion-sdk-py）。

## 安装

```bash
pip install notion-client --break-system-packages
```

## 快速开始

```python
import os
from notion_client import Client

# 初始化客户端
notion = Client(auth=os.environ.get("NOTION_TOKEN"))

# 验证连接
me = notion.users.me()
print(f"Connected as: {me['name']}")
```

## 认证设置

需要 `NOTION_TOKEN` 环境变量。获取方式：
1. 访问 https://www.notion.so/my-integrations
2. 创建 Integration 并复制 Token
3. 在目标页面/数据库中添加 Integration 连接

## 核心操作

### 页面操作

**创建页面**（在数据库中）：
```python
notion.pages.create(
    parent={"database_id": "database_id_here"},
    properties={
        "Name": {"title": [{"text": {"content": "新页面标题"}}]},
        "Status": {"select": {"name": "进行中"}},
        "Due Date": {"date": {"start": "2025-02-01"}}
    },
    children=[  # 可选：添加页面内容
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "内容"}}]
            }
        }
    ]
)
```

**创建子页面**（在页面下）：
```python
notion.pages.create(
    parent={"page_id": "parent_page_id"},
    properties={"title": {"title": [{"text": {"content": "子页面标题"}}]}}
)
```

**更新页面**：
```python
notion.pages.update(
    page_id="page_id",
    properties={"Status": {"select": {"name": "已完成"}}}
)
```

**删除/归档页面**：
```python
notion.pages.update(page_id="page_id", archived=True)
```

### 数据库查询

使用 `data_sources.query()` 查询数据库：

```python
results = notion.data_sources.query(
    data_source_id="database_id",
    filter={
        "and": [
            {"property": "Status", "select": {"equals": "进行中"}},
            {"property": "Priority", "select": {"equals": "高"}}
        ]
    },
    sorts=[{"property": "Due Date", "direction": "ascending"}],
    page_size=100
)

for page in results["results"]:
    title = page["properties"]["Name"]["title"][0]["text"]["content"]
    print(title)
```

**常用过滤器**：参见 [references/filters.md](references/filters.md)

### 块操作

**获取页面内容**：
```python
children = notion.blocks.children.list(block_id="page_id")
for block in children["results"]:
    print(f"Type: {block['type']}")
```

**追加块**：
```python
notion.blocks.children.append(
    block_id="page_id",
    children=[
        {"object": "block", "type": "heading_2", "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "标题"}}]
        }},
        {"object": "block", "type": "paragraph", "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": "段落内容"}}]
        }},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": "列表项"}}]
        }}
    ]
)
```

**块类型参考**：参见 [references/block_types.md](references/block_types.md)

### 搜索

```python
results = notion.search(
    query="关键词",
    filter={"property": "object", "value": "page"},  # 或 "database"
    sort={"direction": "descending", "timestamp": "last_edited_time"}
)
```

### 分页处理

```python
from notion_client.helpers import iterate_paginated_api

# 自动处理分页
for page in iterate_paginated_api(
    notion.data_sources.query,
    data_source_id="database_id"
):
    process(page)
```

手动分页：
```python
start_cursor = None
while True:
    response = notion.data_sources.query(
        data_source_id="database_id",
        start_cursor=start_cursor,
        page_size=100
    )
    for page in response["results"]:
        process(page)
    if not response["has_more"]:
        break
    start_cursor = response["next_cursor"]
```

## 错误处理

```python
from notion_client import APIResponseError, APIErrorCode

try:
    notion.pages.retrieve(page_id="invalid_id")
except APIResponseError as e:
    if e.code == APIErrorCode.ObjectNotFound:
        print("页面不存在或无权访问")
    elif e.code == APIErrorCode.RateLimited:
        print("请求频率限制，稍后重试")
    else:
        print(f"Error: {e.code} - {e.message}")
```

## 常用脚本

- **创建页面**：运行 `scripts/create_page.py`
- **查询数据库**：运行 `scripts/query_database.py`
- **批量更新**：运行 `scripts/batch_update.py`
- **导出数据**：运行 `scripts/export_database.py`

## 参考文档

- **过滤器语法**：[references/filters.md](references/filters.md)
- **块类型详解**：[references/block_types.md](references/block_types.md)
- **属性类型**：[references/property_types.md](references/property_types.md)
