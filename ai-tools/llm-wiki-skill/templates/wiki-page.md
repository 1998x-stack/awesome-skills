---
type:                    # entity | concept | synthesis (必填)
status: active           # active | stale | archived (必填)
confidence:              # 0.0-1.0，基于来源数量估算 (必填)
decay_rate: medium       # slow | medium | fast (默认 medium / default: medium)
created: {{date}}        # 创建日期 (必填)
updated: {{date}}        # 最后更新日期
last_accessed: {{date}}  # 最后被引用日期
source_count:            # 信息来源数量 (必填，≥1)
tags: []                 # 主题标签，如 [数值分析, 迭代法]
aliases: []              # 别名列表，含中英文变体，如 ["Newton's Method", "牛顿迭代"]
relates_to: []           # 关系列表，格式见下方示例
supersedes: null         # 如果此页面取代旧页面，填入旧页面名
---
<!-- relates_to 示例:
relates_to:
  - target: "[[相关页面]]"
    type: extends       # uses|depends_on|contradicts|caused|extends|implements|supersedes|part_of|compares_to
-->

# {{title}}

## 概述
<!-- 50-200 字符，一句话概括核心定义或身份。不要超过 200 字符。 -->

## 关键内容
<!-- 至少 300 字符。分条目阐述核心知识点。使用 [[双链]] 引用相关概念。 -->

1. **要点一**：
2. **要点二**：
3. **要点三**：

## 来源
<!-- 列出所有信息来源，格式：[[source page]] — 具体章节或页码 -->
- [[]] —

## 相关
<!-- 至少 3 个 [[双链]]，标注关系类型 -->
- [[]] — extends
- [[]] — relates_to
- [[]] — relates_to
