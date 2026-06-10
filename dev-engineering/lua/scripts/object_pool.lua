--[[
  object_pool.lua — 泛型对象池
  兼容: Lua 5.1+

  用途: 消除热路径中的频繁内存分配和 GC 压力。
  适合: 子弹、粒子、特效、音效实例、伤害数字等短命对象。

  用法:
    local Pool = require("object_pool")
    
    -- 定义子弹池
    local bullet_pool = Pool.new({
        create = function()
            return {x=0, y=0, vx=0, vy=0, damage=0, alive=false}
        end,
        reset = function(b, x, y, vx, vy, damage)
            b.x=x; b.y=y; b.vx=vx; b.vy=vy
            b.damage=damage; b.alive=true
        end,
        destroy = function(b) end,  -- 可选清理
        initial = 64,
        max = 256,
    })
    
    -- 获取（从池或新建）
    local b = bullet_pool:acquire(player.x, player.y, 400, 0, 10)
    
    -- 归还
    bullet_pool:release(b)
    
    -- 批量更新模式（推荐）
    bullet_pool:each(function(b, dt)
        b.x = b.x + b.vx * dt
        if out_of_bounds(b) then
            return false  -- 返回 false → 自动归还
        end
    end, dt)
--]]

local Pool = {}
Pool.__index = Pool

--- 创建对象池
--- @param opts table
---   opts.create    function()        创建新对象
---   opts.reset     function(obj,...) 重置对象（acquire 时调用）
---   opts.destroy   function(obj)     销毁回调（可选）
---   opts.initial   number            预分配数量（默认 16）
---   opts.max       number            最大对象数（0=无限，默认 0）
--- @return table Pool 实例
function Pool.new(opts)
    assert(type(opts.create) == "function", "Pool requires opts.create function")

    local p = setmetatable({
        _create    = opts.create,
        _reset     = opts.reset  or function() end,
        _destroy   = opts.destroy or function() end,
        _max       = opts.max or 0,
        _free      = {},      -- 空闲列表
        _active    = {},      -- 活跃列表（有序）
        _active_set= {},      -- 活跃集合（快速 release 检查）
        _total     = 0,       -- 总创建数
        _peak      = 0,       -- 历史峰值
    }, Pool)

    -- 预分配
    local initial = opts.initial or 16
    for i = 1, initial do
        local obj = p._create()
        p._free[#p._free + 1] = obj
        p._total = p._total + 1
    end

    return p
end

-- ────────────────────────────────────────────────────
-- 核心操作
-- ────────────────────────────────────────────────────

--- 从池中获取一个对象
--- @param ... any 传给 reset 函数的参数
--- @return table|nil  若超过 max 则返回 nil
function Pool:acquire(...)
    -- 检查上限
    local active_count = #self._active
    if self._max > 0 and active_count >= self._max then
        return nil
    end

    -- 从空闲列表取
    local obj
    if #self._free > 0 then
        obj = table.remove(self._free)
    else
        -- 扩容
        obj = self._create()
        self._total = self._total + 1
    end

    -- 重置状态
    self._reset(obj, ...)

    -- 加入活跃列表
    self._active[#self._active + 1] = obj
    self._active_set[obj] = #self._active

    -- 更新峰值
    local cnt = #self._active
    if cnt > self._peak then self._peak = cnt end

    return obj
end

--- 将对象归还给池
--- @param obj table
--- @return boolean 是否成功（对象必须属于该池）
function Pool:release(obj)
    local idx = self._active_set[obj]
    if not idx then return false end

    -- 从活跃列表 O(1) 删除（尾部交换）
    local n = #self._active
    if idx < n then
        local last = self._active[n]
        self._active[idx] = last
        self._active_set[last] = idx
    end
    self._active[n] = nil
    self._active_set[obj] = nil

    -- 归还到空闲列表
    self._free[#self._free + 1] = obj

    return true
end

--- 遍历所有活跃对象（支持在回调中安全 release）
--- @param fn function(obj, ...) → boolean|nil  返回 false 则自动 release
--- @param ... any 额外传给 fn 的参数
function Pool:each(fn, ...)
    local i = 1
    while i <= #self._active do
        local obj = self._active[i]
        local result = fn(obj, ...)
        if result == false then
            self:release(obj)
            -- release 后 i 位置换成了新对象，不递增
        else
            i = i + 1
        end
    end
end

--- 遍历并收集满足条件的对象（不修改池）
--- @param pred function(obj) → boolean
--- @return table
function Pool:filter(pred)
    local result = {}
    for _, obj in ipairs(self._active) do
        if pred(obj) then result[#result+1] = obj end
    end
    return result
end

--- 归还所有活跃对象
function Pool:release_all()
    for i = #self._active, 1, -1 do
        local obj = self._active[i]
        self._active[i] = nil
        self._active_set[obj] = nil
        self._free[#self._free + 1] = obj
    end
end

--- 销毁池（释放所有引用）
function Pool:destroy()
    for _, obj in ipairs(self._active) do self._destroy(obj) end
    for _, obj in ipairs(self._free)   do self._destroy(obj) end
    self._active = {}
    self._active_set = {}
    self._free = {}
    self._total = 0
end

-- ────────────────────────────────────────────────────
-- 查询
-- ────────────────────────────────────────────────────

--- 活跃对象数量
function Pool:active_count()  return #self._active end
--- 空闲对象数量
function Pool:free_count()    return #self._free end
--- 总创建数量
function Pool:total_count()   return self._total end
--- 历史峰值
function Pool:peak_count()    return self._peak end

--- 打印统计信息
function Pool:print_stats(name)
    print(string.format(
        "[Pool] %s  active=%-4d  free=%-4d  total=%-4d  peak=%-4d",
        name or "?", #self._active, #self._free, self._total, self._peak
    ))
end

-- ────────────────────────────────────────────────────
-- 便捷工厂方法
-- ────────────────────────────────────────────────────

--- 为简单结构创建池（自动 reset 所有字段）
--- @param template table 模板对象（定义字段和默认值）
--- @param initial number|nil
--- @param max number|nil
--- @return table Pool
function Pool.for_struct(template, initial, max)
    local keys = {}
    local defaults = {}
    for k, v in pairs(template) do
        keys[#keys+1] = k
        defaults[k] = v
    end

    return Pool.new({
        create = function()
            local obj = {}
            for _, k in ipairs(keys) do obj[k] = defaults[k] end
            return obj
        end,
        reset = function(obj, overrides)
            for _, k in ipairs(keys) do obj[k] = defaults[k] end
            if overrides then
                for k, v in pairs(overrides) do obj[k] = v end
            end
        end,
        initial = initial or 16,
        max = max or 0,
    })
end

return Pool
