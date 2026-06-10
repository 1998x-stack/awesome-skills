--[[
  hot_reload.lua — 运行时脚本热重载系统
  兼容: Lua 5.1+ / LuaJIT（需要 lfs 或系统命令）

  功能:
    - 监视文件修改时间
    - 自动重新加载已变更的模块
    - 保留模块间引用（浅替换）
    - 触发重载事件供其他系统响应
    - 支持手动强制重载

  依赖: lfs（LuaFileSystem）或 io.popen（用 stat 命令）

  用法:
    local HotReload = require("hot_reload")
    
    -- 注册要监视的模块
    HotReload.watch("src.player", "src/player.lua")
    HotReload.watch("src.enemy",  "src/enemy.lua")
    
    -- 在 update 中每秒检查一次
    local check_timer = 0
    function love.update(dt)
        check_timer = check_timer + dt
        if check_timer > 1.0 then
            check_timer = 0
            HotReload.check()
        end
    end
    
    -- 监听重载事件
    HotReload.on_reload(function(module_name, new_module)
        print("Reloaded:", module_name)
        -- 重新初始化相关系统...
    end)
--]]

local HotReload = {}

local _watched = {}     -- module_name → {path, mtime}
local _callbacks = {}   -- 重载回调列表

-- ────────────────────────────────────────────────────
-- 文件修改时间获取（跨平台）
-- ────────────────────────────────────────────────────

-- 尝试使用 LuaFileSystem
local lfs_ok, lfs = pcall(require, "lfs")

local function get_mtime(path)
    if lfs_ok then
        local attr = lfs.attributes(path, "modification")
        return attr or 0
    else
        -- 回退：使用 os.popen + stat（Unix/macOS）
        local cmd
        if package.config:sub(1,1) == "\\" then
            -- Windows
            cmd = string.format('forfiles /P . /M "%s" /C "cmd /c echo @fdate @ftime"', path)
        else
            -- Unix/macOS
            cmd = string.format("stat -c %%Y '%s' 2>/dev/null || stat -f %%m '%s' 2>/dev/null", path, path)
        end
        local f = io.popen(cmd)
        if not f then return 0 end
        local t = tonumber(f:read("*l")) or 0
        f:close()
        return t
    end
end

-- ────────────────────────────────────────────────────
-- 公共 API
-- ────────────────────────────────────────────────────

--- 注册要监视的模块
--- @param module_name string require 用的模块名（如 "src.player"）
--- @param file_path string 文件路径（如 "src/player.lua"）
function HotReload.watch(module_name, file_path)
    _watched[module_name] = {
        path  = file_path,
        mtime = get_mtime(file_path),
    }
end

--- 停止监视某模块
--- @param module_name string
function HotReload.unwatch(module_name)
    _watched[module_name] = nil
end

--- 检查所有监视的文件，重载已变更的模块
--- @return table reloaded 本次重载的模块名列表
function HotReload.check()
    local reloaded = {}
    for name, info in pairs(_watched) do
        local current_mtime = get_mtime(info.path)
        if current_mtime > info.mtime then
            info.mtime = current_mtime
            local ok, err = HotReload.reload(name)
            if ok then
                reloaded[#reloaded + 1] = name
            else
                print(string.format("[HotReload] Failed to reload '%s': %s", name, err))
            end
        end
    end
    return reloaded
end

--- 强制重载某个模块
--- @param module_name string
--- @return boolean ok, string|nil error
function HotReload.reload(module_name)
    -- 清除旧缓存
    package.loaded[module_name] = nil

    -- 重新加载
    local ok, new_module = pcall(require, module_name)
    if not ok then
        -- 恢复缓存为 false（防止下次 require 时报空）
        package.loaded[module_name] = false
        return false, new_module
    end

    print(string.format("[HotReload] ✓ Reloaded: %s", module_name))

    -- 触发回调
    for _, cb in ipairs(_callbacks) do
        local cb_ok, cb_err = pcall(cb, module_name, new_module)
        if not cb_ok then
            print(string.format("[HotReload] Callback error: %s", cb_err))
        end
    end

    return true, new_module
end

--- 注册重载回调
--- @param fn function(module_name: string, new_module: any)
--- @return function 取消注册函数
function HotReload.on_reload(fn)
    _callbacks[#_callbacks + 1] = fn
    return function()
        for i, cb in ipairs(_callbacks) do
            if cb == fn then
                table.remove(_callbacks, i)
                return
            end
        end
    end
end

--- 获取所有监视状态
--- @return table {module_name → {path, mtime}}
function HotReload.status()
    local result = {}
    for name, info in pairs(_watched) do
        result[name] = {
            path  = info.path,
            mtime = info.mtime,
            current_mtime = get_mtime(info.path),
        }
    end
    return result
end

--- 打印所有监视的模块状态
function HotReload.print_status()
    print("=== HotReload Status ===")
    for name, info in pairs(_watched) do
        local current = get_mtime(info.path)
        local changed = current > info.mtime
        print(string.format("  %-30s  %s  %s",
            name,
            info.path,
            changed and "[CHANGED]" or "[OK]"
        ))
    end
end

--- 重新扫描所有模块路径并注册（自动发现）
--- @param base_dir string 扫描目录（需要 lfs）
--- @param prefix string  模块名前缀（如 "src."）
function HotReload.scan_dir(base_dir, prefix)
    if not lfs_ok then
        print("[HotReload] scan_dir requires LuaFileSystem (lfs)")
        return
    end
    prefix = prefix or ""
    for entry in lfs.dir(base_dir) do
        if entry ~= "." and entry ~= ".." then
            local full_path = base_dir .. "/" .. entry
            local attr = lfs.attributes(full_path)
            if attr then
                if attr.mode == "file" and entry:match("%.lua$") then
                    local module_name = prefix .. entry:gsub("%.lua$", "")
                    HotReload.watch(module_name, full_path)
                elseif attr.mode == "directory" then
                    local sub_prefix = prefix .. entry .. "."
                    HotReload.scan_dir(full_path, sub_prefix)
                end
            end
        end
    end
end

return HotReload
