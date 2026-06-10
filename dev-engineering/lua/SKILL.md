---
name: lua
description: >
  专业 Lua 脚本开发与游戏引擎集成专家技能。当用户需要编写 Lua 代码、调试 Lua 脚本、
  将 Lua 嵌入 C/C++ 引擎、理解 Lua C API 绑定、开发 LÖVE2D/Roblox/Defold/Cocos2d-x/
  Unity(MoonSharp/NLua) 游戏、实现 Lua OOP/协程/事件系统/沙盒、LuaJIT 性能优化、
  Luau 类型系统、以及任何 Lua 语言问题时必须激活此技能。
  即使用户只说"帮我写个 Lua 脚本"、"Roblox 怎么通信"、"怎么在 C++ 里调 Lua"、
  "love2d 怎么做碰撞"、"Lua 协程怎么用"也应立即激活。
  覆盖 Lua 5.1 / 5.2 / 5.3 / 5.4 / LuaJIT / Luau 全版本。
---

# Lua 专家技能

## 概述

本技能覆盖 Lua 语言及其与游戏引擎集成的全部知识域，提供生产级代码模板、
调试策略和架构决策指导。优先产出可直接运行的完整代码，而非片段。

## 核心知识结构

### 立即可用的参考文件（按需加载）

| 文件 | 内容 | 何时读取 |
|------|------|---------|
| `references/lua-c-api.md` | C API 完整参考、栈操作、绑定模式 | C/C++ 嵌入 Lua、自定义引擎 |
| `references/engine-integration.md` | 各引擎集成模式对比、代码示例 | LÖVE/Roblox/Defold/Unity/CryEngine |
| `references/patterns.md` | OOP、协程、事件、沙盒、热重载 | 架构设计、高级模式 |
| `references/luau-types.md` | Luau 类型系统、Roblox 特有 API | Roblox 开发 |
| `references/performance.md` | LuaJIT/FFI、GC 调优、对象池 | 性能优化 |

### 可直接执行的脚本模板

| 脚本 | 用途 |
|------|------|
| `scripts/class_system.lua` | 经典 OOP / 组件系统 |
| `scripts/event_bus.lua` | 事件/信号发布订阅系统 |
| `scripts/coroutine_scheduler.lua` | 协程任务调度器 |
| `scripts/sandbox.lua` | 安全沙盒执行环境 |
| `scripts/hot_reload.lua` | 运行时热重载系统 |
| `scripts/object_pool.lua` | 对象池（GC 优化） |
| `scripts/state_machine.lua` | 层次状态机 |
| `scripts/c_binding_template.c` | C 绑定完整模板 |
| `scripts/love2d_starter.lua` | LÖVE2D 完整游戏模板 |
| `scripts/roblox_remote.lua` | Roblox 远程通信模板 |

---

## 快速决策树

```
用户问题类型？
├── "怎么在 C/C++ 里用 Lua" / "引擎嵌入"
│   → 读 references/lua-c-api.md + scripts/c_binding_template.c
│
├── "LÖVE2D" / "love2d" / "love."
│   → 读 references/engine-integration.md#love2d + scripts/love2d_starter.lua
│
├── "Roblox" / "Luau" / "RemoteEvent" / "Studio"
│   → 读 references/luau-types.md + scripts/roblox_remote.lua
│
├── "Defold" / "msg.post" / "go." / ".script"
│   → 读 references/engine-integration.md#defold
│
├── "Unity" / "MoonSharp" / "NLua" / "C#"
│   → 读 references/engine-integration.md#unity
│
├── "OOP" / "类" / "继承" / "组件"
│   → 读 scripts/class_system.lua 直接使用或改写
│
├── "协程" / "coroutine" / "wait" / "异步"
│   → 读 scripts/coroutine_scheduler.lua
│
├── "性能" / "LuaJIT" / "FFI" / "GC" / "内存"
│   → 读 references/performance.md
│
└── 一般 Lua 问题
    → 直接回答，必要时参考 patterns.md
```

---

## 代码质量标准

生成代码时始终遵循：

1. **模块化**：每个文件返回一个模块表，不污染全局
2. **错误处理**：关键操作用 `pcall`/`xpcall` 包裹
3. **注释风格**：复杂逻辑必须有中文注释说明意图
4. **版本兼容**：明确标注 Lua 版本要求（5.1/5.4/LuaJIT/Luau）
5. **性能意识**：热路径局部化全局变量、避免不必要的表创建
6. **类型文档**：函数参数和返回值注明类型（LDoc 风格或 Luau 类型）

---

## 常见问题速查

**Q: Lua 数组从几开始？**  
A: **1**（不是 0）。`#` 操作符只对无空洞的连续数组可靠。

**Q: 为什么修改函数参数中的表没有效果？**  
A: 重新赋值 `t = {}` 只改局部变量。用 `for k in pairs(t) do t[k]=nil end` 清空。

**Q: `require` vs `dofile` vs `load`？**  
A: `require` 有缓存（`package.loaded`）且搜索路径；`dofile` 每次执行；`load` 编译字符串/函数为 chunk。

**Q: Lua 5.1 vs 5.4 主要差异？**  
A: 5.4 增加整数类型、分代 GC、`<const>/<close>` 属性；Roblox Luau 基于 5.1 分支。

**Q: `local function f()` vs `local f = function()`？**  
A: 前者函数名在函数体内可见（可递归）；后者在赋值完成前不可见。

---

## 响应策略

- **提供完整可运行的代码**，而非仅片段
- **引擎特有代码**：明确标注引擎名和版本
- **涉及 C 绑定**：同时提供 C 侧和 Lua 侧代码
- **性能敏感**：主动指出潜在的 GC 压力点
- **Roblox 代码**：注意 Server/Client 安全边界，永远在服务端验证客户端输入
