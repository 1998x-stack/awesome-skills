---
name: prefab-search
description: >
  Game prefab resource semantic search. Given ANY user description — no matter how vague,
  colloquial, or in Chinese — finds the top 3 most relevant prefab assets from the resource
  library and returns their uuid, name, and description.
  TRIGGER when: user asks to "find a resource", "find a prefab", "I need a model for...",
  "give me something that looks like...", "推荐一个资源", "找一个prefab", "我需要一个...",
  "帮我找", or any natural-language description of a game asset they're looking for.
  Works with colloquial, imprecise, cross-language queries.
---

# Prefab Resource Semantic Search

You help users find the most relevant prefab assets from a curated game resource library
using natural language. The library contains **355 prefabs** across 13 categories.

## How to Execute (Always Follow This Order)

### Step 1 — Understand the Query

Interpret the user's intent even if vague or colloquial. Extract:
- **What kind of object/creature** is needed
- **Style preferences** (卡通/写实/像素/低多边形/科幻 etc.)
- **Use context** (RPG怪物 / 养成宠物 / 场景摆件 / 建筑构件 etc.)
- **Functional needs** (需要动画? 需要战斗动作? 只是场景装饰?)

### Step 2 — Coarse Ranking: Select Categories

Pick **1–3 categories** from the index below that best match the query.
Then READ the corresponding `references/cat-XX.md` files.

Do NOT read all 13 files — only the selected ones. This keeps token cost low.

**When in doubt between two categories, read both** — fine-ranking will resolve it.

### Step 3 — Fine Ranking: Pick Top 3

From the resources in the loaded reference files, select the **3 best matches**.

Ranking criteria (in order of importance):
1. **语义匹配** — tags, description, use_cases 与用户意图的语义契合度
2. **风格契合** — 用户提到的美术风格（卡通/写实/像素等）
3. **功能完整性** — 如果用户需要动画，优先选有完整动画的资源
4. **相似度去重** — 避免返回3个几乎相同的资源；尽量覆盖不同变体

### Step 4 — Return Results

Return results in this exact format:

```
## 推荐资源

### 1. {名称}
- **UUID**: `{uuid}`
- **描述**: {一句话描述，说明为什么推荐}
- **标签**: {相关标签}
- **动画**: {动画类型，如无则写"静态道具"}

### 2. {名称}
...

### 3. {名称}
...

> 匹配逻辑: {一句话说明你选了哪些类目，以及主要匹配依据}
```

---

## Category Index（13 个类目）

| ID | 类目名称 | 关键词 | 资源数 |
|----|---------|--------|--------|
| CAT-01 | **奇幻幻想生物** | 龙、精灵、神兽、魔法生物、飞龙、幻想怪物 | 47 |
| CAT-02 | **卡通萌宠** | Q版宠物、萌系小动物、可爱、养成、情感互动 | 26 |
| CAT-03 | **怪物战斗单位** | 游戏怪物、boss、战斗NPC、地精、恐龙怪物 | 14 |
| CAT-04 | **野生动物** | 写实动物、猩猩、鲨鱼、鸟类、海洋生物、昆虫 | 14 |
| CAT-05 | **人形角色** | 玩家角色、NPC、人物、战士、小男孩、少女 | 34 |
| CAT-06 | **植被植物** | 树木、灌木、花草、蘑菇、植物、薰衣草 | 29 |
| CAT-07 | **岩石地貌** | 岩石、石块、地貌装饰、石头堆、碎石 | 19 |
| CAT-08 | **建筑构件** | 建筑、墙、门、屋顶、广告牌、围墙、模块化 | 33 |
| CAT-09 | **生活道具** | 日常物品、家具、灯、箱子、道具、标识牌、装饰 | 52 |
| CAT-10 | **工业机械科技** | 管道、机械臂、工业设备、电器、科幻道具 | 36 |
| CAT-11 | **武器装备** | 武器、法杖、大炮、枪、刀剑、头盔 | 12 |
| CAT-12 | **载具** | 汽车、飞行器、重型车辆、交通工具 | 9 |
| CAT-13 | **几何基础体** | 方块、几何体、长方体、基础形状、像素砖块 | 30 |

---

## Category Definitions & Decision Rules

Use these rules to decide which category to route to. When a query is ambiguous, the
**primary distinction** is usually creature vs. prop vs. character.

### CAT-01 奇幻幻想生物
龙类、飞龙、精灵、神兽、幻想属性生物（火焰狐、月狼、独角兽等）。
区别于 CAT-02：奇幻色彩强，通常有战斗动画；CAT-02 更侧重萌和日常互动。
区别于 CAT-03：CAT-01 多为中立/宠物/BOSS属性；CAT-03 专指游戏中的敌人怪物。
→ 触发词: 龙、飞龙、精灵、神兽、奇幻生物、魔法生物、幻想怪物

### CAT-02 卡通萌宠
Q版/卡通风格的小动物和宠物，情感互动动画丰富（Caress/Eat/Sleep等），适合养成系统。
→ 触发词: 宠物、萌宠、可爱的小动物、养成、陪伴、Q版小动物

### CAT-03 怪物战斗单位
明确作为游戏敌人的怪物，战斗逻辑完整（Attack/Hit/Die），如地精、蜘蛛、暗影牛怪。
→ 触发词: 游戏怪物、敌人、boss、战斗怪、小兵、NPC怪物、地牢怪物

### CAT-04 野生动物
写实或半写实的现实动物（猩猩、鲨鱼、河马、鸵鸟、海狸等）。
区别于 CAT-02：风格更写实，不那么Q版；且多为野生属性而非宠物属性。
→ 触发词: 真实动物、野生动物、写实动物、海洋生物、鸟类

### CAT-05 人形角色
人类或拟人角色，包含玩家角色、NPC、卡通人物、Q版小人等。
→ 触发词: 角色、人物、玩家、NPC、小男孩、少女、战士、角色素体

### CAT-06 植被植物
树木、灌木、花草、蘑菇等植物资源，多为静态场景装饰物。
→ 触发词: 树、植物、花、草丛、灌木、薰衣草、蘑菇、藤蔓、枯树

### CAT-07 岩石地貌
各类岩石、石块堆、地表碎石，用于自然场景装饰。
→ 触发词: 岩石、石块、石头、碎石堆、地貌装饰

### CAT-08 建筑构件
建筑相关组件：墙体、屋顶、门、广告牌、围墙、支柱等。
→ 触发词: 建筑、墙、门、屋顶、广告牌、招牌、围墙、构件、建筑模块

### CAT-09 生活道具
日常生活场景中的道具：家具、灯具、容器、路灯、标识、装饰品等。
→ 触发词: 道具、家具、灯、箱子、路灯、标识牌、日用品、场景装饰

### CAT-10 工业机械科技
工业风/科幻风：管道、机械臂、工业设备、家用电器、科幻球体等。
→ 触发词: 管道、机械、工业、机械臂、电器、科幻道具、设备、科技

### CAT-11 武器装备
武器类道具：法杖、大炮、枪支部件、刀剑、头盔等。
→ 触发词: 武器、法杖、大炮、枪、剑、装备、头盔

### CAT-12 载具
交通工具：跑车、重型车辆、飞行器等。
→ 触发词: 载具、汽车、车辆、飞行器、飞机、卡车

### CAT-13 几何基础体
基础几何形状：方块、长方体、圆柱、像素砖块等抽象形状。
→ 触发词: 几何体、方块、长方体、基础形状、砖块、低多边形几何

---

## Routing Examples

| 用户输入 | 路由类目 |
|---------|---------|
| "找个可爱的小动物，有互动动画" | CAT-02 |
| "我想要一个龙" | CAT-01 |
| "游戏里的小怪，能打架那种" | CAT-03 |
| "真实一点的大猩猩" | CAT-04 |
| "RPG的主角角色" | CAT-05 |
| "场景里的树" | CAT-06 |
| "地上放几块石头" | CAT-07 |
| "建筑的门和墙" | CAT-08 |
| "街边的路灯" | CAT-09 |
| "工厂里的管道" | CAT-10 |
| "魔法棒" | CAT-11 |
| "一辆红色跑车" | CAT-12 |
| "测试用的方块" | CAT-13 |
| "科幻风格的小动物，能战斗" | CAT-01 + CAT-02 |
| "低多边形的小怪" | CAT-03（style filter in fine ranking） |
| "像素风格的树" | CAT-06（style filter in fine ranking） |

---

## Token Cost Guide

- 每个 reference 文件约 3,000–6,000 tokens
- 每次查询建议读 1–2 个类目文件，最多 3 个
- 对于跨类目的模糊查询，先选最可能的1个类目，若无合适结果再扩展

---

## Reference Files

所有资源按类目分布在 `references/` 目录：

- `references/cat-01.md` — 奇幻幻想生物（47条）
- `references/cat-02.md` — 卡通萌宠（26条）
- `references/cat-03.md` — 怪物战斗单位（14条）
- `references/cat-04.md` — 野生动物（14条）
- `references/cat-05.md` — 人形角色（34条）
- `references/cat-06.md` — 植被植物（29条）
- `references/cat-07.md` — 岩石地貌（19条）
- `references/cat-08.md` — 建筑构件（33条）
- `references/cat-09.md` — 生活道具（52条）
- `references/cat-10.md` — 工业机械科技（36条）
- `references/cat-11.md` — 武器装备（12条）
- `references/cat-12.md` — 载具（9条）
- `references/cat-13.md` — 几何基础体（30条）

每条资源格式：
```
### 资源名称
- uuid: `UUID字符串`
- 标签: tag1, tag2, ...
- 使用场景: 场景A / 场景B
- 描述: 简短描述
- 风格: 美术风格 | 动画: 动画分类列表（无则"无"）
```
