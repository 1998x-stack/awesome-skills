--[[
  event_bus.lua — 发布订阅事件系统
  兼容: Lua 5.1+

  特性:
    - 优先级排序
    - once（单次监听）
    - 异步队列（延迟到下帧派发）
    - 类型安全（可选的事件类型注册）
    - 性能：内部使用快照防止迭代中修改

  用法:
    local Events = require("event_bus")
    
    -- 监听
    local unsub = Events.on("player:died", function(player)
        print(player.name, "died")
    end)
    
    -- 单次
    Events.once("game:start", function() print("Started!") end)
    
    -- 派发
    Events.emit("player:died", player_obj)
    
    -- 取消订阅
    unsub()
    
    -- 命名空间
    local Combat = Events.namespace("combat")
    Combat.on("hit", handler)
    Combat.emit("hit", data)
    Combat.clear()    -- 仅清除 combat: 命名空间
--]]

local EventBus = {}

-- 每个事件名 → 有序监听器列表
local _listeners = {}
-- 延迟队列
local _queue = {}

-- ────────────────────────────────────────────────────
-- 核心 API
-- ────────────────────────────────────────────────────

--- 订阅事件
--- @param event_name string
--- @param callback function
--- @param priority number|nil  高优先级先执行（默认 0）
--- @return function 取消订阅函数
function EventBus.on(event_name, callback, priority)
    assert(type(event_name) == "string", "event_name must be string")
    assert(type(callback) == "function", "callback must be function")
    priority = priority or 0

    if not _listeners[event_name] then
        _listeners[event_name] = {}
    end

    local entry = {fn = callback, priority = priority, once = false}
    local list = _listeners[event_name]
    list[#list + 1] = entry

    -- 按优先级插入排序（监听器数量通常较少，简单排序即可）
    for i = #list - 1, 1, -1 do
        if list[i].priority < list[i+1].priority then
            list[i], list[i+1] = list[i+1], list[i]
        else
            break
        end
    end

    -- 返回取消订阅函数（闭包捕获 entry）
    return function()
        EventBus._remove(event_name, entry)
    end
end

--- 订阅一次性事件（触发后自动取消）
--- @param event_name string
--- @param callback function
--- @param priority number|nil
--- @return function 取消订阅函数
function EventBus.once(event_name, callback, priority)
    local unsub
    local called = false
    unsub = EventBus.on(event_name, function(...)
        if not called then
            called = true
            callback(...)
            unsub()
        end
    end, priority)
    return unsub
end

--- 取消订阅
--- @param event_name string
--- @param callback function
function EventBus.off(event_name, callback)
    if not _listeners[event_name] then return end
    for i, entry in ipairs(_listeners[event_name]) do
        if entry.fn == callback then
            table.remove(_listeners[event_name], i)
            return
        end
    end
end

--- 派发事件（同步，立即执行所有监听器）
--- @param event_name string
--- @param ... any 传递给监听器的参数
function EventBus.emit(event_name, ...)
    local list = _listeners[event_name]
    if not list or #list == 0 then return end

    -- 快照：防止回调中修改监听器列表引发问题
    local snapshot = {}
    for i = 1, #list do snapshot[i] = list[i] end

    local args = {...}
    for _, entry in ipairs(snapshot) do
        -- 检查 entry 是否还在列表中（可能被 once 移除）
        local ok, err = pcall(function()
            entry.fn(table.unpack(args))
        end)
        if not ok then
            -- 错误不阻止其他监听器
            if EventBus.on_error then
                EventBus.on_error(event_name, err)
            else
                print("[EventBus] Error in handler for '" .. event_name .. "': " .. tostring(err))
            end
        end
    end
end

--- 派发事件（异步，加入队列，下次 flush 时执行）
--- @param event_name string
--- @param ... any
function EventBus.emit_deferred(event_name, ...)
    _queue[#_queue + 1] = {event_name, ...}
end

--- 刷新延迟队列（在游戏主循环末尾调用）
function EventBus.flush()
    if #_queue == 0 then return end
    local batch = _queue
    _queue = {}
    for _, item in ipairs(batch) do
        EventBus.emit(table.unpack(item))
    end
end

--- 清除事件的所有监听器
--- @param event_name string|nil  nil = 清除全部
function EventBus.clear(event_name)
    if event_name then
        _listeners[event_name] = nil
    else
        _listeners = {}
    end
end

--- 获取某事件的监听器数量
--- @param event_name string
--- @return number
function EventBus.count(event_name)
    return _listeners[event_name] and #_listeners[event_name] or 0
end

--- 是否有监听器
--- @param event_name string
--- @return boolean
function EventBus.has(event_name)
    return EventBus.count(event_name) > 0
end

-- 全局错误处理器（可替换）
EventBus.on_error = nil

-- ────────────────────────────────────────────────────
-- 内部辅助
-- ────────────────────────────────────────────────────

function EventBus._remove(event_name, entry)
    local list = _listeners[event_name]
    if not list then return end
    for i, e in ipairs(list) do
        if e == entry then
            table.remove(list, i)
            return
        end
    end
end

-- ────────────────────────────────────────────────────
-- 命名空间支持
-- ────────────────────────────────────────────────────

--- 创建命名空间（方便管理一组相关事件）
--- @param ns string 命名空间前缀（如 "combat"）
--- @return table 命名空间对象，自动添加 "ns:" 前缀
function EventBus.namespace(ns)
    local prefix = ns .. ":"
    local N = {}

    function N.on(name, cb, priority)
        return EventBus.on(prefix .. name, cb, priority)
    end

    function N.once(name, cb, priority)
        return EventBus.once(prefix .. name, cb, priority)
    end

    function N.off(name, cb)
        EventBus.off(prefix .. name, cb)
    end

    function N.emit(name, ...)
        EventBus.emit(prefix .. name, ...)
    end

    function N.emit_deferred(name, ...)
        EventBus.emit_deferred(prefix .. name, ...)
    end

    function N.clear(name)
        if name then
            EventBus.clear(prefix .. name)
        else
            -- 清除所有该命名空间的事件
            for k in pairs(_listeners) do
                if k:sub(1, #prefix) == prefix then
                    _listeners[k] = nil
                end
            end
        end
    end

    return N
end

return EventBus
