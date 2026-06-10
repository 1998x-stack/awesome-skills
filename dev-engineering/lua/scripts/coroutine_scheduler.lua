--[[
  coroutine_scheduler.lua — 协程任务调度器
  兼容: Lua 5.1+ / LuaJIT
  
  让游戏脚本可以用线性方式编写时序逻辑，无需状态机。
  
  全局辅助函数（可选 require 后注入）:
    wait(seconds)           -- 暂停指定秒数
    wait_frames(n)          -- 等待 n 帧
    wait_until(fn)          -- 等到条件为 true
    wait_event(name)        -- 等到事件触发
  
  用法:
    local Scheduler = require("coroutine_scheduler")
    
    -- 在 love.load / init 中注入全局等待函数（可选）
    Scheduler.inject_globals()
    
    -- 在 love.update(dt) / update(dt) 中驱动
    Scheduler.update(dt)
    
    -- 派生任务
    Scheduler.spawn(function()
        entity:play_anim("attack")
        wait(0.5)
        entity:deal_damage(target, 25)
        wait(0.3)
        entity:play_anim("idle")
    end)
    
    -- 延迟任务
    Scheduler.after(3.0, function()
        spawn_wave(level + 1)
    end)
    
    -- 每帧任务（返回 false 停止）
    Scheduler.every(0.5, function()
        spawn_particle(x, y)
        return game_running  -- 若为 false 则停止
    end)
--]]

local Scheduler = {}

-- 全局时间（由 update 驱动）
local _time = 0.0
local _frame = 0
local _tasks = {}
local _task_id = 0
local _event_waiters = {}  -- 事件名 → {coroutine列表}

-- 调度器关联的事件总线（可选，用于 wait_event）
local _event_bus = nil

-- ────────────────────────────────────────────────────
-- 内部辅助
-- ────────────────────────────────────────────────────

local function new_task(co, resume_at, args)
    _task_id = _task_id + 1
    return {
        id       = _task_id,
        co       = co,
        resume_at = resume_at or _time,
        args     = args,
        active   = true,
    }
end

local function resume_task(task, ...)
    local ok, result = coroutine.resume(task.co, ...)
    if not ok then
        -- 错误：打印并终止任务
        if Scheduler.on_error then
            Scheduler.on_error(result, task)
        else
            print(string.format("[Scheduler] Task #%d error: %s", task.id, tostring(result)))
        end
        task.active = false
        return
    end
    if coroutine.status(task.co) == "dead" then
        task.active = false
    else
        -- result = 下次唤醒时间（绝对时间）
        task.resume_at = result or _time
    end
end

-- ────────────────────────────────────────────────────
-- 协程内可调用的等待函数（通过 coroutine.yield 实现）
-- ────────────────────────────────────────────────────

--- 等待指定秒数（在协程内调用）
local function wait(seconds)
    coroutine.yield(_time + (seconds or 0))
end

--- 等待 n 帧（在协程内调用）
local function wait_frames(n)
    n = n or 1
    local target_frame = _frame + n
    while _frame < target_frame do
        coroutine.yield(_time)  -- 每帧都检查
    end
end

--- 等待条件为 true（在协程内调用）
local function wait_until(condition_fn)
    while not condition_fn() do
        coroutine.yield(_time)  -- 下帧继续检查
    end
end

--- 等待事件（需设置 event_bus，在协程内调用）
local function wait_event(event_name)
    if not _event_bus then
        error("wait_event requires Scheduler.set_event_bus(bus)", 2)
    end
    local co = coroutine.running()
    _event_waiters[event_name] = _event_waiters[event_name] or {}
    _event_waiters[event_name][#_event_waiters[event_name]+1] = co
    coroutine.yield(math.huge)  -- 无限等待，直到被事件唤醒
end

-- ────────────────────────────────────────────────────
-- 公共 API
-- ────────────────────────────────────────────────────

--- 派生新任务
--- @param fn function 协程函数（内部可使用 wait/wait_frames 等）
--- @param ... any 传给 fn 的初始参数
--- @return table task 句柄（可用于 cancel）
function Scheduler.spawn(fn, ...)
    local co = coroutine.create(fn)
    local task = new_task(co, _time, {...})
    _tasks[#_tasks + 1] = task
    return task
end

--- 延迟执行
--- @param delay number 延迟秒数
--- @param fn function
--- @param ... any
--- @return table task
function Scheduler.after(delay, fn, ...)
    local args = {...}
    return Scheduler.spawn(function()
        wait(delay)
        fn(table.unpack(args))
    end)
end

--- 周期性执行（fn 返回 false 停止）
--- @param interval number 间隔秒数
--- @param fn function 函数（返回 false 停止）
--- @param ... any
--- @return table task
function Scheduler.every(interval, fn, ...)
    local args = {...}
    return Scheduler.spawn(function()
        while true do
            local result = fn(table.unpack(args))
            if result == false then break end
            wait(interval)
        end
    end)
end

--- 取消任务
--- @param task table
function Scheduler.cancel(task)
    if task then task.active = false end
end

--- 主更新（在游戏主循环中调用）
--- @param dt number 帧时间（秒）
function Scheduler.update(dt)
    _time = _time + dt
    _frame = _frame + 1

    -- 遍历并更新所有任务
    local i = 1
    local n = #_tasks
    while i <= n do
        local task = _tasks[i]
        if not task.active then
            -- 移除已完成/取消的任务
            _tasks[i] = _tasks[n]
            _tasks[n] = nil
            n = n - 1
        elseif _time >= task.resume_at then
            if task.args then
                local args = task.args
                task.args = nil
                resume_task(task, table.unpack(args))
            else
                resume_task(task)
            end
            if task.active then i = i + 1 end
        else
            i = i + 1
        end
    end
end

--- 触发事件（唤醒所有 wait_event 等待者）
--- @param event_name string
--- @param ... any 传给等待的协程
function Scheduler.emit(event_name, ...)
    local waiters = _event_waiters[event_name]
    if not waiters or #waiters == 0 then return end
    
    local args = {...}
    local resolved = {}
    for _, co in ipairs(waiters) do
        -- 找到对应 task 并立即唤醒
        for _, task in ipairs(_tasks) do
            if task.co == co and task.active then
                task.resume_at = _time  -- 下次 update 立即执行
                -- 将事件参数注入（暂存在 task.event_args）
                task.event_args = args
                break
            end
        end
        resolved[#resolved+1] = co
    end
    
    -- 移除已解除等待的协程
    _event_waiters[event_name] = nil
end

--- 设置关联的事件总线（用于 wait_event）
--- @param bus table 实现 on/emit 接口的事件总线
function Scheduler.set_event_bus(bus)
    _event_bus = bus
end

--- 将 wait/wait_frames/wait_until/wait_event 注入全局环境
--- 只在脚本中作为约定使用，不推荐在模块中用
function Scheduler.inject_globals(env)
    env = env or _G
    env.wait        = wait
    env.wait_frames = wait_frames
    env.wait_until  = wait_until
    env.wait_event  = wait_event
    env.spawn       = function(fn, ...) return Scheduler.spawn(fn, ...) end
end

--- 获取当前调度器状态
--- @return table {time, frame, task_count}
function Scheduler.stats()
    return {
        time = _time,
        frame = _frame,
        task_count = #_tasks,
    }
end

--- 清除所有任务（场景切换时用）
function Scheduler.clear()
    _tasks = {}
    _event_waiters = {}
    _time = 0
    _frame = 0
end

--- 重置时间（保留任务）
function Scheduler.reset_time()
    -- 调整所有任务的 resume_at
    local delta = -_time
    for _, task in ipairs(_tasks) do
        if task.resume_at < math.huge then
            task.resume_at = task.resume_at + delta
        end
    end
    _time = 0
    _frame = 0
end

-- 暴露等待函数供外部使用（在协程内调用）
Scheduler.wait        = wait
Scheduler.wait_frames = wait_frames
Scheduler.wait_until  = wait_until
Scheduler.wait_event  = wait_event

-- 全局错误处理器（可替换）
Scheduler.on_error = nil

return Scheduler
