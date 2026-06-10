# 关系类型定义

relates_to 中 type 字段的合法值。

| 类型 | 语义 | 方向 | 示例 |
|------|------|------|------|
| uses | A 使用 B | A → B | PyTorch uses CUDA |
| depends_on | A 依赖 B | A → B | 项目 depends_on Redis |
| contradicts | A 与 B 矛盾 | 双向 | 论文 A contradicts 论文 B |
| caused | A 导致 B | A → B | Bug caused 数据丢失 |
| extends | A 扩展 B | A → B | v2 extends v1 |
| implements | A 实现 B | A → B | agentmemory implements LLM Wiki |
| supersedes | A 取代 B | A → B | 新方案 supersedes 旧方案 |
| part_of | A 是 B 的一部分 | A → B | 模块 part_of 系统 |
| compares_to | A 与 B 可比较 | 双向 | CLIP compares_to BLIP-2 |

## 使用原则

- 优先选择最具体的关系类型
- 每个关系必须有 confidence 值
- 矛盾关系 (contradicts) 必须附带 note 说明具体矛盾点
- supersedes 关系必须同时更新被取代页面的 supersedes 字段
