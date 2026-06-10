--[[
  state_machine.lua — 层次有限状态机（HFSM）
  兼容: Lua 5.1+

  特性:
    - 嵌套状态（父状态共享行为）
    - enter/exit/update 钩子
    - 条件转移
    - 历史状态（返回上次子状态）
    - 调试模式（打印转移日志）

  用法:
    local HSM = require("state_machine")
    
    local fsm = HSM.new(owner)
    
    fsm:state("idle", {
        enter  = function(self) self.owner:play("idle") end,
        update = function(self, dt) end,
        exit   = function(self) end,
    })
    
    fsm:state("run", {
        enter  = function(self) self.owner:play("run") end,
        update = function(self, dt)
            self.owner:move(dt)
        end,
    })
    
    fsm:state("combat", {}, function(combat)
        combat:state("attack", { enter = ... })
        combat:state("dodge",  { enter = ... })
        combat:initial("attack")
    end)
    
    fsm:transition("idle", "run",    function(fsm) return fsm.owner.speed > 0 end)
    fsm:transition("run",  "idle",   function(fsm) return fsm.owner.speed == 0 end)
    fsm:transition("*",    "combat", function(fsm) return fsm.owner.in_combat end)
    
    fsm:initial("idle")
    fsm:start()
    
    -- 每帧更新
    fsm:update(dt)
    
    -- 手动转移
    fsm:goto("run")
--]]

local HSM = {}
HSM.__index = HSM

--- 创建状态机
--- @param owner any 状态机的拥有者（传给状态回调）
--- @return table 状态机实例
function HSM.new(owner)
    local sm = setmetatable({
        owner        = owner,
        _states      = {},
        _transitions = {},
        _current     = nil,
        _current_path= {},   -- 当前状态路径（含父状态）
        _initial     = nil,
        _debug       = false,
    }, HSM)
    return sm
end

-- ────────────────────────────────────────────────────
-- 状态定义
-- ────────────────────────────────────────────────────

--- 定义一个状态
--- @param name string 状态名
--- @param handlers table {enter, exit, update, on_message}
--- @param children_fn function|nil 子状态配置函数（用于嵌套）
--- @return table 状态对象（支持链式调用）
function HSM:state(name, handlers, children_fn)
    local s = {
        name     = name,
        enter    = handlers.enter,
        exit     = handlers.exit,
        update   = handlers.update,
        on_msg   = handlers.on_message,
        parent   = self._current_parent,  -- 父状态
        _children= {},
        _trans   = {},
        _initial = nil,
        _history = nil,
    }
    self._states[name] = s

    -- 处理子状态
    if children_fn then
        local prev_parent = self._current_parent
        self._current_parent = s
        children_fn(self)
        self._current_parent = prev_parent
    end

    return s
end

--- 设置默认初始状态
--- @param name string
function HSM:initial(name)
    if self._current_parent then
        self._current_parent._initial = name
    else
        self._initial = name
    end
end

-- ────────────────────────────────────────────────────
-- 转移定义
-- ────────────────────────────────────────────────────

--- 添加转移条件
--- @param from string 源状态名（"*" = 任意状态）
--- @param to string   目标状态名
--- @param condition function(sm) → boolean
--- @param priority number|nil  高优先级先检查（默认 0）
function HSM:transition(from, to, condition, priority)
    self._transitions[#self._transitions + 1] = {
        from      = from,
        to        = to,
        condition = condition,
        priority  = priority or 0,
    }
    -- 按优先级排序
    table.sort(self._transitions, function(a, b)
        return a.priority > b.priority
    end)
end

-- ────────────────────────────────────────────────────
-- 运行时
-- ────────────────────────────────────────────────────

--- 启动状态机
function HSM:start()
    assert(self._initial, "No initial state set. Call fsm:initial('state_name')")
    self:goto(self._initial)
end

--- 强制转移到指定状态
--- @param name string 目标状态名
--- @param ... any 传给 enter 的额外参数
function HSM:goto(name, ...)
    local target = self._states[name]
    assert(target, "Unknown state: " .. tostring(name))

    -- 退出当前状态（从叶到根）
    if self._current then
        if self._debug then
            print(string.format("[FSM] %s → %s", self._current.name, name))
        end
        local cur = self._current
        while cur do
            if cur.exit then cur.exit(self) end
            cur = cur.parent
        end
    end

    -- 记录历史
    if self._current and self._current.parent then
        self._current.parent._history = self._current.name
    end

    -- 进入新状态（从根到叶）
    self._current = target
    local chain = {}
    local c = target
    while c do
        table.insert(chain, 1, c)
        c = c.parent
    end
    for _, s in ipairs(chain) do
        if s.enter then s.enter(self, ...) end
    end

    -- 如果目标状态有子状态，进入初始子状态
    if target._initial then
        self:goto(target._history or target._initial)
    end
end

--- 每帧更新（检查转移 + 调用 update）
--- @param dt number
function HSM:update(dt)
    if not self._current then return end

    -- 检查自动转移
    local cur_name = self._current.name
    for _, t in ipairs(self._transitions) do
        if (t.from == "*" or t.from == cur_name) and t.to ~= cur_name then
            local ok, result = pcall(t.condition, self)
            if ok and result then
                self:goto(t.to)
                return  -- 转移后跳过本帧 update
            end
        end
    end

    -- 调用当前状态链的 update（从根到叶）
    local c = self._current
    local chain = {}
    while c do
        table.insert(chain, 1, c)
        c = c.parent
    end
    for _, s in ipairs(chain) do
        if s.update then s.update(self, dt) end
    end
end

--- 发送消息给当前状态
--- @param msg string
--- @param ... any
function HSM:send(msg, ...)
    if self._current and self._current.on_msg then
        self._current.on_msg(self, msg, ...)
    end
end

--- 获取当前状态名
--- @return string|nil
function HSM:current_name()
    return self._current and self._current.name
end

--- 是否处于某状态（或其子状态）
--- @param name string
--- @return boolean
function HSM:is(name)
    local c = self._current
    while c do
        if c.name == name then return true end
        c = c.parent
    end
    return false
end

--- 开启调试输出
function HSM:set_debug(enabled)
    self._debug = enabled
end

return HSM
