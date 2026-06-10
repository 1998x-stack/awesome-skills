# 实体类型定义

wiki/entities/ 中的页面必须属于以下类型之一。

| 类型 | 说明 | 示例 |
|------|------|------|
| person | 人物 | 黄仁勋、Karpathy |
| company | 公司/组织 | 腾讯、OpenAI |
| project | 项目/产品 | Claude Code、agentmemory |
| tool | 工具/库/框架 | CLIP、PyTorch、Obsidian |
| paper | 论文 | GameDevBench |
| book | 书籍 | 深入理解计算机系统 |

## Frontmatter 扩展

entity 页面在通用 frontmatter 基础上增加：

```yaml
entity_type: person | company | project | tool | paper | book
```

## 命名规则

- 中文名为主标题，英文名放 aliases
- 公司用全称，缩写放 aliases
- 人物用最常用的名字
