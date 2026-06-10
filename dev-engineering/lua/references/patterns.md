# Lua 高级模式参考

## 目录
1. [OOP 模式全集](#1-oop-模式全集)
2. [函数式编程模式](#2-函数式编程模式)
3. [元表魔法](#3-元表魔法)
4. [协程模式](#4-协程模式)
5. [模块系统](#5-模块系统)
6. [配置与数据驱动](#6-配置与数据驱动)

---

## 1. OOP 模式全集

### 轻量级 OOP（推荐）

```lua
-- 简洁高效，无需第三方库
local Animal = {}
Animal.__index = Animal

function Animal.new(name, sound)
    return setmetatable({
        name = name,
        sound = sound,
        hp = 100
    }, Animal)
end

function Animal:speak()
    return self.name .. " says " .. self.sound
end

function Animal:take_damage(amount)
    self.hp = math.max(0, self.hp - amount)
    return self.hp
end

function Animal:is_alive() return self.hp > 0 end

-- 继承
local Dog = setmetatable({}, {__index = Animal})
Dog.__index = Dog

function Dog.new(name)
    local self = Animal.new(name, "Woof")
    self.tricks = {}
    return setmetatable(self, Dog)
end

function Dog:learn_trick(trick)
    table.insert(self.tricks, trick)
end

function Dog:perform()
    if #self.tricks == 0 then return "No tricks!" end
    return self.name .. " performs: " .. self.tricks[math.random(#self.tricks)]
end

-- 使用
local d = Dog.new("Rex")
d:learn_trick("sit")
d:learn_trick("roll over")
print(d:speak())    -- Rex says Woof
print(d:perform())  -- Rex performs: sit
```

### 完整继承链（middleclass 风格）

```lua
local function create_class(parent)
    local cls = {}
    cls.__index = cls
    
    if parent then
        setmetatable(cls, {
            __index = parent,
            __call = function(c, ...)
                local inst = setmetatable({}, c)
                if inst.new then inst:new(...) end
                return inst
            end
        })
        cls.super = parent
    else
        setmetatable(cls, {
            __call = function(c, ...)
                local inst = setmetatable({}, c)
                if inst.new then inst:new(...) end
                return inst
            end
        })
    end
    
    cls.is_a = function(self, klass)
        local m = getmetatable(self)
        while m do
            if m == klass then return true end
            m = getmetatable(m) and getmetatable(m).__index
        end
        return false
    end
    
    return cls
end

-- 使用
local Entity = create_class()
function Entity:new(x, y) self.x = x; self.y = y end

local Player = create_class(Entity)
function Player:new(x, y, name)
    Player.super.new(self, x, y)
    self.name = name
    self.hp = 100
end

local p = Player(100, 200, "Hero")
print(p:is_a(Player))   -- true
print(p:is_a(Entity))   -- true
```

### Mixin 混入模式

```lua
local function mixin(target, ...)
    for _, source in ipairs({...}) do
        for k, v in pairs(source) do
            if target[k] == nil then
                target[k] = v
            end
        end
    end
    return target
end

-- Mixin 定义
local Serializable = {
    serialize = function(self)
        local parts = {}
        for k, v in pairs(self) do
            if type(v) ~= "function" then
                parts[#parts+1] = k .. "=" .. tostring(v)
            end
        end
        return "{" .. table.concat(parts, ",") .. "}"
    end
}

local Collidable = {
    collides_with = function(self, other)
        return math.abs(self.x - other.x) < self.w/2 + other.w/2 and
               math.abs(self.y - other.y) < self.h/2 + other.h/2
    end
}

-- 应用 Mixin
local Sprite = create_class()
mixin(Sprite, Serializable, Collidable)
```

---

## 2. 函数式编程模式

```lua
local F = {}

-- map: 变换每个元素
function F.map(t, fn)
    local result = {}
    for i, v in ipairs(t) do result[i] = fn(v, i) end
    return result
end

-- filter: 过滤元素
function F.filter(t, pred)
    local result = {}
    for _, v in ipairs(t) do
        if pred(v) then result[#result+1] = v end
    end
    return result
end

-- reduce: 折叠
function F.reduce(t, fn, init)
    local acc = init
    for _, v in ipairs(t) do acc = fn(acc, v) end
    return acc
end

-- compose: 函数组合（右到左）
function F.compose(...)
    local fns = {...}
    return function(x)
        local result = x
        for i = #fns, 1, -1 do
            result = fns[i](result)
        end
        return result
    end
end

-- pipe: 函数管道（左到右）
function F.pipe(...)
    local fns = {...}
    return function(x)
        local result = x
        for _, fn in ipairs(fns) do result = fn(result) end
        return result
    end
end

-- curry: 柯里化
function F.curry(fn, arity)
    arity = arity or debug.getinfo(fn, "u").nparams
    local function curried(args)
        if #args >= arity then
            return fn(table.unpack(args))
        end
        return function(...)
            local new_args = {table.unpack(args)}
            for _, v in ipairs({...}) do new_args[#new_args+1] = v end
            return curried(new_args)
        end
    end
    return curried({})
end

-- memoize: 记忆化
function F.memoize(fn)
    local cache = {}
    return function(...)
        local key = table.concat({...}, ",")
        if cache[key] == nil then
            cache[key] = fn(...)
        end
        return cache[key]
    end
end

-- 使用示例
local nums = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
local even_squares = F.pipe(
    function(t) return F.filter(t, function(x) return x % 2 == 0 end) end,
    function(t) return F.map(t, function(x) return x * x end) end
)(nums)
-- {4, 16, 36, 64, 100}

local fib = F.memoize(function(n)
    if n <= 1 then return n end
    return fib(n-1) + fib(n-2)  -- 自引用需要先声明 local fib
end)
```

---

## 3. 元表魔法

```lua
-- __index 作为函数（懒加载）
local lazy = setmetatable({}, {
    __index = function(t, k)
        print("Computing " .. k)
        local val = expensive_computation(k)
        rawset(t, k, val)  -- 缓存结果
        return val
    end
})

-- __newindex 拦截赋值（只读表）
local readonly = setmetatable({x = 1, y = 2}, {
    __newindex = function(t, k, v)
        error("Attempt to modify read-only table: " .. k, 2)
    end
})

-- __call 让表可调用
local Vector = setmetatable({}, {
    __call = function(cls, x, y)
        return setmetatable({x=x, y=y}, Vector)
    end
})
Vector.__index = Vector
function Vector:length() return math.sqrt(self.x^2 + self.y^2) end
function Vector:__tostring() return string.format("Vec(%g,%g)", self.x, self.y) end
function Vector:__add(b) return Vector(self.x+b.x, self.y+b.y) end
function Vector:__sub(b) return Vector(self.x-b.x, self.y-b.y) end
function Vector:__mul(s)
    if type(s) == "number" then return Vector(self.x*s, self.y*s) end
    return self.x*s.x + self.y*s.y  -- 点积
end
function Vector:__unm() return Vector(-self.x, -self.y) end
function Vector:__eq(b) return self.x==b.x and self.y==b.y end
function Vector:__len() return self:length() end  -- # 操作符

local v1 = Vector(3, 4)  -- 调用 __call
print(#v1)               -- 5.0（__len）
print(v1 + Vector(1,0))  -- Vec(4,4)（__add + __tostring）

-- __index 链（原型继承）
local defaults = {speed = 100, hp = 100, damage = 10}
local Player = setmetatable({hp = 150}, {__index = defaults})
print(Player.speed)   -- 100 (从 defaults)
print(Player.hp)      -- 150 (Player 自己的)

-- __pairs / __ipairs (Lua 5.2+)
local filtered = setmetatable(data, {
    __pairs = function(t)
        local function iter(t, k)
            local nk, nv = next(t, k)
            while nk and nv < 0 do  -- 跳过负数
                nk, nv = next(t, nk)
            end
            return nk, nv
        end
        return iter, t, nil
    end
})
```

---

## 4. 协程模式

### 生产者-消费者

```lua
local function producer(data)
    return coroutine.wrap(function()
        for _, item in ipairs(data) do
            coroutine.yield(item)
        end
    end)
end

local gen = producer({10, 20, 30, 40})
for item in gen do
    print("Processing:", item)
end
```

### 异步任务序列（游戏中最常用）

```lua
-- 任务系统：协程使游戏脚本看起来是线性的
local task_queue = {}

local function spawn_task(fn, ...)
    local co = coroutine.create(fn)
    local args = {...}
    table.insert(task_queue, {co=co, args=args, timer=0})
end

local function update_tasks(dt)
    local i = 1
    while i <= #task_queue do
        local task = task_queue[i]
        task.timer = task.timer - dt
        if task.timer <= 0 then
            local ok, result
            if task.args then
                ok, result = coroutine.resume(task.co, table.unpack(task.args))
                task.args = nil
            else
                ok, result = coroutine.resume(task.co)
            end
            
            if not ok then
                print("Task error:", result)
                table.remove(task_queue, i)
            elseif coroutine.status(task.co) == "dead" then
                table.remove(task_queue, i)
            else
                -- result 是等待时间
                task.timer = result or 0
                i = i + 1
            end
        else
            i = i + 1
        end
    end
end

-- 使用：线性编写复杂时序逻辑
spawn_task(function()
    print("Boss appears!")
    coroutine.yield(2.0)   -- 等 2 秒
    
    print("Boss attacks!")
    for i = 1, 5 do
        fire_projectile()
        coroutine.yield(0.3)
    end
    
    print("Boss enrages!")
    set_speed_multiplier(2)
    coroutine.yield(5.0)
    
    print("Boss dies!")
    play_death_animation()
end)
```

### 管道（Pipeline）

```lua
-- 协程管道：数据流处理
local function pipeline(source, ...)
    local filters = {...}
    
    -- 将每个 filter 包装成协程
    local coros = {source}
    for _, f in ipairs(filters) do
        table.insert(coros, coroutine.wrap(f))
    end
    
    -- 执行管道
    local data = coros[1]()
    for i = 2, #coros do
        data = coros[i](data)
    end
    return data
end
```

---

## 5. 模块系统

```lua
-- 标准模块模式
local M = {}

-- 私有状态（模块闭包内）
local _private_state = {}
local _config = {debug = false}

-- 公共接口
function M.init(options)
    for k, v in pairs(options or {}) do
        _config[k] = v
    end
end

function M.create(...)
    -- ...
end

-- 带版本的模块
M._VERSION = "1.2.0"
M._DESCRIPTION = "My Game Module"

return M

-- 惰性加载模式（避免循环依赖）
local function get_dependency()
    local dep = require("other_module")
    get_dependency = function() return dep end  -- 替换自己（只加载一次）
    return dep
end

-- 使用模式：项目统一入口
-- init.lua
local Game = {}
Game.Entity  = require("src.entity")
Game.Physics = require("src.physics")
Game.Audio   = require("src.audio")
Game.Input   = require("src.input")
Game.UI      = require("src.ui")

function Game.init()
    Game.Physics.init({gravity = 9.8})
    Game.Audio.init({volume = 0.8})
    Game.Input.init()
end

return Game
```

---

## 6. 配置与数据驱动

```lua
-- 游戏配置表（纯数据，无代码）
-- config/enemies.lua
return {
    goblin = {
        hp = 30,
        speed = 120,
        damage = 8,
        reward = 5,
        sprite = "goblin.png",
        drop_table = {
            {item = "gold", chance = 0.8, amount = {1, 5}},
            {item = "potion", chance = 0.1, amount = {1, 1}},
        }
    },
    troll = {
        hp = 200,
        speed = 60,
        damage = 35,
        reward = 20,
        sprite = "troll.png",
        abilities = {"regeneration", "boulder_throw"},
    }
}

-- 数据驱动的工厂
local EnemyConfig = require("config.enemies")

local function spawn_enemy(type_name, x, y)
    local cfg = EnemyConfig[type_name]
    assert(cfg, "Unknown enemy type: " .. type_name)
    
    return {
        type = type_name,
        hp = cfg.hp,
        max_hp = cfg.hp,
        speed = cfg.speed,
        damage = cfg.damage,
        x = x, y = y,
        sprite = load_sprite(cfg.sprite)
    }
end

-- 技能系统（数据+行为分离）
local SkillDB = {
    fireball = {
        name = "Fireball",
        cost = 20,
        cooldown = 2.0,
        execute = function(caster, target)
            local dmg = caster.magic_power * 2.5
            deal_damage(target, dmg, "fire")
            create_effect("fireball_hit", target.x, target.y)
        end
    },
    heal = {
        name = "Heal",
        cost = 30,
        cooldown = 5.0,
        execute = function(caster, target)
            target = target or caster
            local amount = caster.magic_power * 3
            target.hp = math.min(target.max_hp, target.hp + amount)
        end
    }
}

-- 本地化字符串
local Locale = {}

function Locale.load(lang)
    local ok, data = pcall(require, "locale." .. lang)
    if ok then
        Locale._strings = data
    else
        Locale._strings = require("locale.en")  -- 回退到英语
    end
end

function Locale.get(key, ...)
    local s = Locale._strings[key] or key
    if select("#", ...) > 0 then
        return string.format(s, ...)
    end
    return s
end

-- locale/zh.lua
return {
    ["menu.start"]    = "开始游戏",
    ["menu.options"]  = "设置",
    ["hud.hp"]        = "生命: %d/%d",
    ["dialog.npc_01"] = "勇者，欢迎来到这个世界！",
}
```
