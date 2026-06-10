# API 接口完整规范

## 接口端点

```
GET https://zhibo.sina.com.cn/api/zhibo/feed
```

## 请求参数完整表

| 参数 | 类型 | 必须 | 默认 | 说明 |
|------|------|------|------|------|
| `zhibo_id` | int | ✅ | - | 频道ID，财经固定 152 |
| `tag_id` | int | ✅ | 0 | 分类 ID |
| `page` | int | ✅ | 1 | 页码 |
| `pagesize` | int | ✅ | 20 | 每页条数 |
| `page_size` | int | - | 20 | 同 pagesize，两者均传 |
| `dire` | str | ✅ | f | f=最新方向，b=历史方向 |
| `dpc` | int | ✅ | 1 | 固定传 1 |
| `id` | int | 可选 | - | 游标 ID（增量拉取用） |
| `type` | int | 可选 | 0 | 内容类型过滤 |
| `callback` | str | 可选 | - | JSONP 回调名，不传返回纯 JSON |
| `_` | int | 可选 | - | Unix 毫秒时间戳，防缓存 |

## 分类 tag_id 完整映射

| tag_id | 中文 | 英文 key | 说明 |
|--------|------|----------|------|
| 0 | 全部 | all | 所有分类合并流 |
| 1 | 宏观 | macro | 宏观经济、政策 |
| 2 | 行业 | industry | 行业动态 |
| 3 | 公司 | company | 上市公司、财报 |
| 5 | 市场 | market | 行情、价格变动 |
| 8 | 其他 | other | 未分类 |
| 9 | 焦点 | focus | 热点聚焦 |
| 10 | A股 | a_share | A 股专项 |
| 102 | 国际 | international | 国际财经 |

## 响应体结构

```json
{
  "result": {
    "status": {"code": 0, "msg": "OK"},
    "timestamp": "Fri Mar 06 00:49:04 +0800 2026",
    "data": {
      "feed": {
        "list": [ ...条目数组... ],
        "page_info": {
          "totalPage": 45,
          "pageSize": 20,
          "prePage": 1,
          "nextPage": 2,
          "totalNum": 900,
          "page": 1
        },
        "max_id": 4720477,
        "min_id": 4720458
      }
    }
  }
}
```

## 条目字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 全局唯一 ID（单调递增） |
| `type` | int | 0=纯文本，1=图文 |
| `rich_text` | str | 正文内容 |
| `multimedia` | str/dict | 图片信息（type=1 时为 `{"img_url": [...]}`) |
| `create_time` | str | 创建时间（北京时间） |
| `update_time` | str | 更新时间 |
| `is_delete` | int | 0=正常，1=软删除 |
| `is_repeat` | str | "1"=重复内容 |
| `tag` | list | 分类标签数组 `[{"id":"102","name":"国际"}]` |
| `ext` | str | **JSON 字符串**，含股票引用和文章链接 |
| `docurl` | str | 移动端文章链接 |
| `like_nums` | int | 点赞数 |
| `comment_list` | dict | 评论摘要 |

## ext 字段结构（二次 JSON 解析）

```json
{
  "stocks": [
    {
      "market": "cn",        // 市场标识
      "symbol": "sh600519",  // 股票代码
      "key": "贵州茅台"       // 显示名
    }
  ],
  "needPushWB": false,
  "needCMSLink": true,
  "docurl": "https://finance.sina.com.cn/7x24/.../doc-xxx.shtml",
  "docid": "nhpyimf6386875"
}
```

## market 字段取值

| 值 | 含义 |
|----|------|
| `cn` | A 股（沪深京） |
| `hk` | 港股 |
| `us` | 美股 |
| `global` | 全球期货/现货 |
| `fund` | 基金/ETF |
| `commodity` | 国内商品期货 |
| `CFF` | 中金所期货 |
| `worldIndex` | 全球指数 |

## 分页策略

### 传统页码

```python
page=1 → page=2 → page=3 ...
```

### 游标分页（推荐实时采集）

```python
# 首次：不传 id
GET .../feed?page=1&dire=f

# 增量：传上次的 max_id
GET .../feed?id={max_id}&dire=f&page=1

# 历史回溯：传 min_id + dire=b
GET .../feed?id={min_id}&dire=b&page=1
```

## 反爬建议

| 策略 | 建议值 |
|------|--------|
| User-Agent | 真实 Chrome UA |
| Referer | `https://finance.sina.com.cn/` |
| 请求间隔 | ≥ 500ms |
| 并发数 | ≤ 2 |
| 时段限制 | 无 |

## 已知限制

- 单分类历史深度约 100 条（5 页）
- 不支持 WebSocket，需主动轮询
- 评论完整数据需另调评论接口
- 无需登录 Cookie
