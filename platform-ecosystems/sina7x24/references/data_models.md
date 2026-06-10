# 数据模型参考

## FeedItem — 单条新闻条目

```python
@dataclass
class FeedItem:
    id: int                # 全局唯一 ID
    tag_id: int            # 分类 ID
    tag_name: str          # 分类中文名
    content_type: int      # 0=纯文本，1=图文
    text: str              # 正文内容（已清洗）
    images: list[str]      # 图片 URL 列表
    create_time: str       # "2026-03-06 00:48:08"
    update_time: str       # 最后更新时间
    is_deleted: bool       # 软删除标记
    is_repeat: bool        # 重复内容标记
    tags: list[str]        # ["国际", "市场"]
    stocks: list[StockRef] # 关联股票
    doc_url: str           # PC 端完整文章链接
    doc_id: str            # 文章 ID
    like_nums: int         # 点赞数
    raw: dict              # 原始 API 响应（repr 中隐藏）
```

## StockRef — 股票引用

```python
@dataclass
class StockRef:
    market: str  # "cn"/"hk"/"us"/"global"/"fund"/...
    symbol: str  # "sh600519" / "nvda" / "hf_xau"
    key: str     # "贵州茅台" / "英伟达" / "黄金"
```

## FeedPage — 一页响应

```python
@dataclass
class FeedPage:
    items: list[FeedItem]  # 当前页条目
    max_id: int            # 最新条目 ID（用于游标）
    min_id: int            # 最旧条目 ID（用于历史回溯）
    total_num: int         # 该分类总条数
    total_pages: int       # 总页数
    current_page: int      # 当前页码
    server_time: str       # 服务器时间
```

## 导出格式

### JSON（列表）
```json
[
  {
    "id": 4720477,
    "tag_id": 0,
    "tag_name": "全部",
    "content_type": 0,
    "text": "以色列驻联合国特使表示...",
    "images": [],
    "create_time": "2026-03-06 00:48:08",
    "update_time": "2026-03-06 00:49:02",
    "is_deleted": false,
    "is_repeat": false,
    "tags": ["国际"],
    "stocks": [{"market": "worldIndex", "symbol": "znb_ta-35", "key": "以色列"}],
    "doc_url": "https://finance.sina.com.cn/7x24/.../doc-xxx.shtml",
    "doc_id": "nhpyimf6386875",
    "like_nums": 0
  }
]
```

### JSONL（每行一条，适合流式写入）
```
{"id": 4720477, "text": "...", ...}
{"id": 4720476, "text": "...", ...}
```

### CSV 列名
```
id, tag_name, create_time, text, tags, stocks, doc_url, like_nums, is_deleted, is_repeat
```

## 常用操作示例

```python
from sina7x24_playwright import Sina7x24Client, DataExporter, TAG_MAP

# 过滤有关联股票的快讯
with Sina7x24Client() as client:
    items = list(client.fetch_all(tag_id=TAG_MAP["a_share"], limit=100))

stock_items = [i for i in items if i.stocks]
print(f"含股票引用: {len(stock_items)}/{len(items)}")

# 提取所有提到的股票
all_stocks = set()
for item in items:
    for s in item.stocks:
        all_stocks.add((s.market, s.symbol, s.key))

# 按时间排序
items.sort(key=lambda x: x.create_time, reverse=True)

# 多格式导出
DataExporter.to_json(items, "news.json")
DataExporter.to_jsonl(items, "news.jsonl")
DataExporter.to_csv(items, "news.csv")
DataExporter.to_markdown(items, "news.md")
```
