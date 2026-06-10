--[[
  class_system.lua — Lua OOP 类系统 + 组件架构
  兼容: Lua 5.1 / 5.2 / 5.3 / 5.4 / LuaJIT / Luau
  
  使用方式：
    local Class = require("class_system")
    
    local Animal = Class.define()
    function Animal:init(name) self.name = name end
    function Animal:speak() return self.name .. " speaks" end
    
    local Dog = Class.extend(Animal)
    function Dog:init(name) Animal.init(self, name); self.tricks = {} end
    function Dog:learn(t) self.tricks[#self.tricks+1] = t end
    
    local d = Dog("Rex")
    d:learn("sit")
    print(d:speak())   -- Rex speaks
    print(d:is_a(Dog))    -- true
    print(d:is_a(Animal)) -- true
--]]

local Class = {}

--- 创建一个新类
--- @param parent table|nil 父类
--- @return table 新类
function Class.define(parent)
    local cls = {}
    cls.__index = cls

    -- 支持 is_a 类型检查
    function cls:is_a(klass)
        local m = getmetatable(self)
        while m do
            if m == klass then return true end
            local mt = getmetatable(m)
            m = mt and mt.__index
        end
        return false
    end

    -- 支持 instanceof（is_a 的别名）
    cls.instanceof = cls.is_a

    if parent then
        setmetatable(cls, {
            __index = parent,
            __call = function(c, ...)
                local inst = setmetatable({}, c)
                if inst.init then inst:init(...) end
                return inst
            end
        })
        cls.super = parent
    else
        setmetatable(cls, {
            __call = function(c, ...)
                local inst = setmetatable({}, c)
                if inst.init then inst:init(...) end
                return inst
            end
        })
    end

    return cls
end

--- 从父类派生子类（extend 语法糖）
--- @param parent table 父类
--- @return table 子类
function Class.extend(parent)
    return Class.define(parent)
end

--- 混入（将源的所有非函数+函数字段混入目标）
--- @param target table 目标类
--- @param ... table 一个或多个 mixin 源
--- @return table target（链式调用）
function Class.mixin(target, ...)
    for _, source in ipairs({...}) do
        for k, v in pairs(source) do
            if target[k] == nil then
                target[k] = v
            end
        end
    end
    return target
end

--- 检查对象是否是某类的实例
--- @param obj any
--- @param klass table
--- @return boolean
function Class.isinstance(obj, klass)
    if type(obj) ~= "table" then return false end
    return obj:is_a(klass)
end

-- ────────────────────────────────────────────────────
-- 组件系统
-- ────────────────────────────────────────────────────

--- 基础组件
local Component = Class.define()

function Component:init(owner)
    self.owner = owner
    self.enabled = true
end

function Component:update(dt) end
function Component:draw() end
function Component:on_add() end     -- 加入 Entity 时调用
function Component:on_remove() end  -- 从 Entity 移除时调用

--- 基础实体
local Entity = Class.define()

function Entity:init(x, y)
    self.x = x or 0
    self.y = y or 0
    self.active = true
    self.components = {}
    self._comp_map = {}  -- 类 → 组件 的快速查找表
    self.tags = {}
end

--- 添加组件
--- @param ComponentClass table 组件类
--- @param ... any 传给组件 init 的额外参数
--- @return table 新组件实例
function Entity:add(ComponentClass, ...)
    local comp = ComponentClass(self, ...)
    table.insert(self.components, comp)
    -- 记录到快速查找表（同类组件只记最后一个，如需多个请用 get_all）
    self._comp_map[ComponentClass] = comp
    comp:on_add()
    return comp
end

--- 获取组件（精确匹配）
--- @param ComponentClass table
--- @return table|nil
function Entity:get(ComponentClass)
    return self._comp_map[ComponentClass]
end

--- 获取组件（包含子类，较慢）
--- @param ComponentClass table
--- @return table|nil
function Entity:get_any(ComponentClass)
    for _, comp in ipairs(self.components) do
        if comp:is_a(ComponentClass) then return comp end
    end
    return nil
end

--- 获取所有同类组件
--- @param ComponentClass table
--- @return table
function Entity:get_all(ComponentClass)
    local result = {}
    for _, comp in ipairs(self.components) do
        if getmetatable(comp) == ComponentClass or comp:is_a(ComponentClass) then
            result[#result+1] = comp
        end
    end
    return result
end

--- 移除组件
--- @param comp table 组件实例
function Entity:remove(comp)
    for i, c in ipairs(self.components) do
        if c == comp then
            comp:on_remove()
            table.remove(self.components, i)
            -- 从 map 中移除
            for cls, ref in pairs(self._comp_map) do
                if ref == comp then
                    self._comp_map[cls] = nil
                    break
                end
            end
            return
        end
    end
end

--- 是否有某标签
--- @param tag string
--- @return boolean
function Entity:has_tag(tag)
    return self.tags[tag] == true
end

--- 添加标签
function Entity:add_tag(tag)
    self.tags[tag] = true
end

--- 移除标签
function Entity:remove_tag(tag)
    self.tags[tag] = nil
end

function Entity:update(dt)
    if not self.active then return end
    for _, comp in ipairs(self.components) do
        if comp.enabled then comp:update(dt) end
    end
end

function Entity:draw()
    if not self.active then return end
    for _, comp in ipairs(self.components) do
        if comp.enabled and comp.draw then comp:draw() end
    end
end

function Entity:destroy()
    for _, comp in ipairs(self.components) do
        comp:on_remove()
    end
    self.components = {}
    self._comp_map = {}
    self.active = false
end

-- ────────────────────────────────────────────────────
-- 实体管理器
-- ────────────────────────────────────────────────────

local World = Class.define()

function World:init()
    self.entities = {}
    self._by_tag = {}
    self._pending_add = {}
    self._pending_remove = {}
end

function World:add(entity)
    -- 缓冲区：在帧末统一添加（避免迭代中修改）
    self._pending_add[#self._pending_add + 1] = entity
end

function World:remove(entity)
    self._pending_remove[entity] = true
end

function World:_flush()
    -- 处理待添加
    for _, e in ipairs(self._pending_add) do
        self.entities[#self.entities + 1] = e
        for tag in pairs(e.tags) do
            self._by_tag[tag] = self._by_tag[tag] or {}
            self._by_tag[tag][#self._by_tag[tag]+1] = e
        end
    end
    self._pending_add = {}

    -- 处理待移除
    if next(self._pending_remove) then
        local n = #self.entities
        local i = 1
        while i <= n do
            if self._pending_remove[self.entities[i]] then
                table.remove(self.entities, i)
                n = n - 1
            else
                i = i + 1
            end
        end
        self._pending_remove = {}
    end
end

function World:update(dt)
    self:_flush()
    for _, e in ipairs(self.entities) do
        if e.active then e:update(dt) end
    end
end

function World:draw()
    for _, e in ipairs(self.entities) do
        if e.active then e:draw() end
    end
end

function World:get_by_tag(tag)
    return self._by_tag[tag] or {}
end

function World:count()
    return #self.entities
end

-- ────────────────────────────────────────────────────
-- 导出
-- ────────────────────────────────────────────────────

Class.Component = Component
Class.Entity = Entity
Class.World = World

return Class
