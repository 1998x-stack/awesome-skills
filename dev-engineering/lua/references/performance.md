# Lua 性能优化参考

## 性能分析原则

1. **先测量，再优化**：使用 `os.clock()` 或 profiler
2. **最大收益点**：局部化全局访问、避免热路径分配、使用对象池
3. **LuaJIT 特规则**：FFI 调用 > C 函数 > 纯 Lua（JIT 后）> 纯 Lua（解释）

---

## GC 调优

```lua
-- Lua 5.1/5.2/5.3 增量 GC
-- pause: 内存增长多少后触发 GC（200 = 翻倍触发）
-- stepmul: 每步处理多少内存（200 = 中等激进）
collectgarbage("setpause", 150)
collectgarbage("setstepmul", 300)

-- Lua 5.4 分代 GC（短生命对象多时更高效）
-- minor_mul: minor GC 频率（20 = 内存增长 20% 触发）
-- major_mul: major GC 频率（200 = major GC 后增长 200% 触发）
collectgarbage("generational", 20, 200)

-- 手动控制 GC（游戏帧内）
collectgarbage("stop")      -- 停止自动 GC
collectgarbage("step", 100) -- 手动步进（100KB 工作量）
collectgarbage("collect")   -- 完整 GC（避免在帧内！）
collectgarbage("count")     -- 返回当前内存 KB

-- 帧预算式 GC（推荐）
local GC = {}
GC.budget_ms = 0.5

function GC.update()
    local t = os.clock()
    while (os.clock() - t) * 1000 < GC.budget_ms do
        if collectgarbage("step", 50) then break end
    end
end
```

---

## LuaJIT FFI 高性能绑定

```lua
local ffi = require("ffi")

-- 声明 C 结构（无 GC，值语义）
ffi.cdef[[
    typedef struct { float x, y, z, w; } Vec4;
    typedef struct { float m[16]; }      Mat4;
    typedef struct {
        float x, y;
        uint16_t u, v;
        uint32_t color;
    } Vertex;
    
    // 引擎函数
    void render_batch(const Vertex *verts, int count);
    int  spawn_particle(float x, float y, float vx, float vy, uint32_t color);
    void set_uniform_mat4(int loc, const Mat4 *m);
]]

-- 高性能顶点缓冲
local MAX_VERTS = 4096
local vbuf = ffi.new("Vertex[?]", MAX_VERTS)
local vert_count = 0

local function add_quad(x, y, w, h, color)
    local i = vert_count
    vbuf[i+0] = {x,   y,   0, 0, color}
    vbuf[i+1] = {x+w, y,   1, 0, color}
    vbuf[i+2] = {x+w, y+h, 1, 1, color}
    vbuf[i+3] = {x,   y+h, 0, 1, color}
    vert_count = vert_count + 4
end

local function flush()
    if vert_count > 0 then
        ffi.C.render_batch(vbuf, vert_count)
        vert_count = 0
    end
end

-- 性能对比：FFI 调用比 lua_pushnumber/lua_call 快 5-10x
```

---

## 对象池

```lua
-- 泛型对象池（防止热路径 GC）
local Pool = {}
Pool.__index = Pool

function Pool.new(template, initial_count)
    local p = setmetatable({
        _free = {},
        _template = template,
        _created = 0,
    }, Pool)
    for i = 1, (initial_count or 16) do
        p:_create()
    end
    return p
end

function Pool:_create()
    local obj = {}
    for k, v in pairs(self._template) do
        if type(v) ~= "function" then obj[k] = v end
    end
    self._created = self._created + 1
    table.insert(self._free, obj)
end

function Pool:acquire()
    if #self._free == 0 then self:_create() end
    return table.remove(self._free)
end

function Pool:release(obj)
    -- 重置为模板值
    for k, v in pairs(self._template) do
        if type(v) ~= "function" then obj[k] = v end
    end
    table.insert(self._free, obj)
end

function Pool:stats()
    return {
        created = self._created,
        free = #self._free,
        active = self._created - #self._free
    }
end

-- 使用
local bullet_pool = Pool.new({
    x=0, y=0, vx=0, vy=0, damage=10, alive=false, lifetime=3.0
}, 64)

-- 创建子弹
local b = bullet_pool:acquire()
b.x, b.y = player.x, player.y
b.vx, b.vy = dir.x * 400, dir.y * 400
b.alive = true

-- 更新
for _, b in ipairs(active_bullets) do
    b.lifetime = b.lifetime - dt
    if b.lifetime <= 0 then
        bullet_pool:release(b)
    end
end
```

---

## 热路径优化清单

```lua
-- ✅ 1. 局部化频繁使用的全局/上值
local sin, cos, sqrt = math.sin, math.cos, math.sqrt
local insert, remove = table.insert, table.remove
local format = string.format
local type, pairs, ipairs = type, pairs, ipairs

-- ✅ 2. 预先计算循环不变量
-- ❌ 慢：
for i = 1, #entities do  -- 每次迭代都查 #entities
    update(entities[i])
end
-- ✅ 快：
local n = #entities
for i = 1, n do
    update(entities[i])
end

-- ✅ 3. 数值 for 比 ipairs 快（LuaJIT 可 JIT 编译）
for i = 1, n do  -- 比 for i, v in ipairs(t) 快约 20%
    local v = t[i]
end

-- ✅ 4. 布尔短路
-- 先检查便宜条件
if is_alive and has_target and can_attack then end

-- ✅ 5. 避免在热路径中创建 table
-- ❌ 慢（每帧 GC 压力）：
function get_bounds(obj)
    return {x=obj.x-obj.w/2, y=obj.y-obj.h/2, w=obj.w, h=obj.h}
end
-- ✅ 快（复用）：
local _bounds = {}
function get_bounds(obj)
    _bounds.x = obj.x - obj.w/2
    _bounds.y = obj.y - obj.h/2
    _bounds.w = obj.w
    _bounds.h = obj.h
    return _bounds
end

-- ✅ 6. 字符串拼接用 table.concat
-- ❌ 慢（O(n²) 内存）：
local s = ""
for i = 1, 1000 do s = s .. items[i] end
-- ✅ 快：
local parts = {}
for i = 1, 1000 do parts[i] = items[i] end
local s = table.concat(parts)

-- ✅ 7. LuaJIT: 偏好 float 算术而非混合类型
-- JIT 可以向量化纯 float 运算

-- ✅ 8. 缓存 method 查找（非常频繁调用时）
local entity_update = Entity.update  -- 缓存方法
for _, e in ipairs(entities) do
    entity_update(e, dt)  -- 比 e:update(dt) 减少一次表查找
end
```

---

## 性能基准测试工具

```lua
local Bench = {}

function Bench.run(name, iterations, fn, ...)
    -- 预热
    for i = 1, math.min(100, iterations / 10) do fn(...) end
    
    collectgarbage("collect")
    collectgarbage("stop")
    
    local mem_before = collectgarbage("count")
    local t0 = os.clock()
    
    for i = 1, iterations do fn(...) end
    
    local elapsed = os.clock() - t0
    local mem_after = collectgarbage("count")
    
    collectgarbage("restart")
    
    print(string.format(
        "[Bench] %-30s  %7d iter  %8.3f ms  %6.1f ns/op  mem: %+.1f KB",
        name, iterations, elapsed * 1000,
        elapsed / iterations * 1e9,
        mem_after - mem_before
    ))
end

-- 使用
Bench.run("table_create", 100000, function()
    local t = {x=1, y=2, z=3}
end)

Bench.run("setmetatable_call", 100000, function()
    local v = Vector.new(1, 2)
end)
```
