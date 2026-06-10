---
name: sina7x24
description: >
  新浪财经 7×24 直播流 API 采集与分析技能。当用户提到新浪财经资讯、7x24财经快讯、A股资讯抓取、财经新闻API、股票相关新闻爬取、实时财经数据、sina finance live feed、7×24小时数据接口分析时，必须使用此技能。涵盖API逆向分析、Python客户端构建、多分类采集（全部/A股/宏观/公司/国际等）、实时轮询、数据导出（CSV/JSON/JSONL/Markdown）等完整工作流。即使用户只是问"如何获取财经资讯"或"怎么分析新浪接口"也应使用。
compatibility: "Python >=3.8 | pip install playwright loguru && playwright install chromium"
---

# 新浪财经 7×24 直播流采集技能

## 快速导航

| 需要做什么 | 去哪里 |
|-----------|--------|
| API 接口参数、字段详解 | `references/api_spec.md` |
| 完整 Python 客户端代码 | `scripts/sina7x24_playwright.py` |
| 快速上手代码片段 | 本文件「快速上手」节 |
| 数据模型 / 导出格式 | `references/data_models.md` |

---

## 接口速查

```
GET https://zhibo.sina.com.cn/api/zhibo/feed
```

### 核心参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `zhibo_id` | 固定=152（财经频道）| `152` |
| `tag_id` | 分类（见下表）| `0` |
| `page` | 页码 | `1` |
| `pagesize` | 每页条数 | `20` |
| `dire` | 方向：f=最新 b=更旧 | `f` |
| `id` | 游标 ID（增量拉取）| `4720477` |

### 分类 tag_id

| tag_id | 分类 | 英文 key |
|--------|------|----------|
| 0 | 全部 | all |
| 1 | 宏观 | macro |
| 2 | 行业 | industry |
| 3 | 公司 | company |
| 5 | 市场 | market |
| 8 | 其他 | other |
| 9 | 焦点 | focus |
| 10 | A股 | a_share |
| 102 | 国际 | international |

---

## 安装

```bash
pip install playwright loguru
playwright install chromium
```

---

## 快速上手

### 1. 单次批量采集

```python
from sina7x24_playwright import Sina7x24Client, DataExporter, TAG_MAP

with Sina7x24Client() as client:
    # 采集 A 股最新 50 条
    items = list(client.fetch_all(tag_id=TAG_MAP["a_share"], limit=50))

DataExporter.to_json(items, "a_share.json")
DataExporter.to_csv(items, "a_share.csv")
```

### 2. 增量实时采集

```python
with Sina7x24Client() as client:
    max_id = None
    while True:
        page = client.fetch_latest(tag_id=0, since_id=max_id)
        for item in page.items:
            print(f"[{item.create_time}] {item.text[:60]}")
        max_id = page.max_id
        time.sleep(60)
```

### 3. 流式采集（自动去重）

```python
with Sina7x24Client() as client:
    for item in client.stream(tag_id=0, interval=60):
        print(f"新快讯: {item.text}")
        DataExporter.append_jsonl(item, "stream.jsonl")
```

### 4. CLI 命令

```bash
# 采集全部，存 JSON
python sina7x24_playwright.py fetch --tag all --limit 100 --output news.json

# A股实时流，写 JSONL
python sina7x24_playwright.py stream --tag a_share --interval 30 --output live.jsonl

# 多分类批量
python sina7x24_playwright.py multi --tags all,macro,international --limit 50
```

---

## 关键数据字段

```python
item.id           # 全局唯一 ID（单调递增）
item.text         # 正文内容
item.create_time  # "2026-03-06 00:48:08"
item.tags         # ["国际", "市场"]
item.stocks       # [StockRef(market="cn", symbol="sh600519", key="贵州茅台")]
item.doc_url      # 完整文章链接
item.images       # 图片 URL 列表（type=1 时）
item.is_deleted   # 软删除标记
```

---

## 深入参考

- **完整字段说明 / ext 解析 / 分页策略** → `references/api_spec.md`
- **FeedItem / FeedPage 数据模型** → `references/data_models.md`
- **生产级 Python 代码（含 CLI）** → `scripts/sina7x24_playwright.py`
