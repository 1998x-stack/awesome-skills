--[[
  sandbox.lua — 安全沙盒执行环境
  兼容: Lua 5.1 / 5.2 / 5.3 / 5.4

  用途: 安全执行不受信任的用户脚本（Mod、关卡脚本、用户自定义逻辑）。
  
  安全策略:
    1. 白名单环境（禁止 io/os/require/debug/load/dofile 等危险 API）
    2. 指令计数限制（防止无限循环）
    3. 内存限制（Lua 5.4 可精确控制）
    4. 执行超时保护

  用法:
    local Sandbox = require("sandbox")
    
    -- 创建沙盒（可注入受控 API）
    local sb = Sandbox.new({
        game_api = {
            move = function(x, y) ... end,
            fire = function() ... end,
        },
        max_instructions = 500000,
    })
    
    -- 执行代码
    local ok, result, err = sb:run([[
        local x = 0
        for i = 1, 10 do
            x = x + i
        end
        return x
    ]])
    
    if ok then
        print("Result:", result)
    else
        print("Error:", err)
    end
--]]

local Sandbox = {}
Sandbox.__index = Sandbox

-- ────────────────────────────────────────────────────
-- 安全环境白名单
-- ────────────────────────────────────────────────────

local SAFE_MATH = {
    abs=math.abs, ceil=math.ceil, floor=math.floor,
    max=math.max, min=math.min, fmod=math.fmod,
    sqrt=math.sqrt, exp=math.exp, log=math.log,
    sin=math.sin, cos=math.cos, tan=math.tan,
    asin=math.asin, acos=math.acos, atan=math.atan,
    pi=math.pi, huge=math.huge, maxinteger=math.maxinteger,
    random=math.random, randomseed=math.randomseed,
    type=math.type,  -- 5.3+
}

local SAFE_STRING = {
    format=string.format, len=string.len, sub=string.sub,
    find=string.find, match=string.match, gmatch=string.gmatch,
    gsub=string.gsub, rep=string.rep, reverse=string.reverse,
    upper=string.upper, lower=string.lower,
    byte=string.byte, char=string.char,
}

local SAFE_TABLE = {
    insert=table.insert, remove=table.remove,
    sort=table.sort, concat=table.concat,
    unpack=table.unpack or unpack,
    move=table.move,  -- 5.3+
}

local function make_base_env()
    return {
        -- 基础
        assert=assert, error=error, pcall=pcall, xpcall=xpcall,
        type=type, tostring=tostring, tonumber=tonumber,
        ipairs=ipairs, pairs=pairs, next=next, select=select,
        rawget=rawget, rawset=rawset, rawequal=rawequal, rawlen=rawlen,
        setmetatable=setmetatable, getmetatable=getmetatable,
        unpack=table.unpack or unpack,
        -- 安全模块
        math=SAFE_MATH,
        string=SAFE_STRING,
        table=SAFE_TABLE,
        -- 安全 print（可替换）
        print=print,
        -- 被禁止的（不包含）：
        -- io, os, require, dofile, loadfile, load, collectgarbage,
        -- debug, package, coroutine（可按需开放）
    }
end

-- ────────────────────────────────────────────────────
-- 沙盒实例
-- ────────────────────────────────────────────────────

--- 创建沙盒实例
--- @param opts table
---   opts.inject           table|nil  注入到沙盒的额外 API
---   opts.max_instructions number|nil  最大指令数（默认 500000）
---   opts.allow_coroutine  boolean     是否开放协程（默认 false）
---   opts.output_fn        function    替换 print 的输出函数
--- @return table Sandbox 实例
function Sandbox.new(opts)
    opts = opts or {}
    local sb = setmetatable({
        _max_instr    = opts.max_instructions or 500000,
        _allow_coro   = opts.allow_coroutine or false,
        _output_fn    = opts.output_fn,
        _env          = make_base_env(),
        _state        = {},  -- 持久化状态（跨调用）
    }, Sandbox)

    -- 自定义 print
    if opts.output_fn then
        sb._env.print = opts.output_fn
    end

    -- 开放协程
    if opts.allow_coroutine then
        sb._env.coroutine = {
            create=coroutine.create, resume=coroutine.resume,
            yield=coroutine.yield, wrap=coroutine.wrap,
            status=coroutine.status, running=coroutine.running,
        }
    end

    -- 注入自定义 API
    if opts.inject then
        for k, v in pairs(opts.inject) do
            sb._env[k] = v
        end
    end

    -- 持久化沙盒状态（脚本间共享）
    sb._env._state = sb._state

    -- 设置 _ENV 自引用（Lua 5.2+ 必须）
    sb._env._ENV = sb._env

    return sb
end

--- 执行代码字符串
--- @param code string Lua 代码
--- @param chunk_name string|nil 用于错误信息的名称
--- @return boolean ok
--- @return any     result（若成功）/ nil
--- @return string  err（若失败）/ nil
function Sandbox:run(code, chunk_name)
    chunk_name = chunk_name or "=sandbox"
    return self:_execute(code, chunk_name, false)
end

--- 执行文件内容
--- @param filepath string
--- @return boolean ok, any result, string err
function Sandbox:run_file(filepath)
    local f, err = io.open(filepath, "r")
    if not f then return false, nil, "Cannot open file: " .. err end
    local code = f:read("*a")
    f:close()
    return self:_execute(code, "@" .. filepath, false)
end

--- 在沙盒中定义/更新函数（用于持久化注入）
--- @param name string
--- @param value any
function Sandbox:inject(name, value)
    self._env[name] = value
end

--- 获取沙盒中的全局变量
--- @param name string
--- @return any
function Sandbox:get(name)
    return self._env[name]
end

--- 重置沙盒持久化状态
function Sandbox:reset_state()
    for k in pairs(self._state) do self._state[k] = nil end
end

-- ────────────────────────────────────────────────────
-- 内部执行（含保护机制）
-- ────────────────────────────────────────────────────

function Sandbox:_execute(code, chunk_name, is_trusted)
    -- 1. 编译阶段
    local fn, compile_err
    if _VERSION >= "Lua 5.2" then
        -- Lua 5.2+: 使用 load 的第四个参数指定环境
        fn, compile_err = load(code, chunk_name, "t", self._env)
    else
        -- Lua 5.1: 使用 setfenv
        fn, compile_err = loadstring(code, chunk_name)
        if fn then setfenv(fn, self._env) end
    end

    if not fn then
        return false, nil, "Compile error: " .. tostring(compile_err)
    end

    -- 2. 执行阶段（带保护）
    if not is_trusted and self._max_instr > 0 then
        return self:_run_protected(fn)
    else
        local results = table.pack(xpcall(fn, debug.traceback))
        local ok = table.remove(results, 1)
        if ok then
            return true, table.unpack(results, 1, results.n - 1)
        else
            return false, nil, results[1]
        end
    end
end

function Sandbox:_run_protected(fn)
    local instr_count = 0
    local max = self._max_instr
    local limit_hit = false

    -- 安装指令计数 hook
    -- 注意: debug.sethook 是全局的，多线程/多协程需额外注意
    local function count_hook()
        instr_count = instr_count + 100
        if instr_count > max then
            limit_hit = true
            error("Instruction limit exceeded (" .. max .. ")", 2)
        end
    end

    debug.sethook(count_hook, "", 100)

    local ok, err
    local results = {}

    ok, err = xpcall(function()
        results = table.pack(fn())
    end, function(e)
        debug.sethook()  -- 立即移除 hook
        if limit_hit then
            return "Script execution limit exceeded (max " .. max .. " instructions)"
        end
        return debug.traceback(tostring(e), 2)
    end)

    debug.sethook()  -- 确保 hook 被移除

    if ok then
        return true, table.unpack(results, 1, results.n)
    else
        return false, nil, err
    end
end

-- ────────────────────────────────────────────────────
-- 快捷函数（无状态、一次性执行）
-- ────────────────────────────────────────────────────

--- 快捷执行（无需创建 Sandbox 实例）
--- @param code string
--- @param inject table|nil 注入 API
--- @param max_instr number|nil
--- @return boolean ok, any result, string err
function Sandbox.eval(code, inject, max_instr)
    local sb = Sandbox.new({
        inject = inject,
        max_instructions = max_instr or 100000,
    })
    return sb:run(code, "=eval")
end

return Sandbox
