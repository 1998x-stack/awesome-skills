--[[
  roblox_remote.lua — Roblox 远程通信完整模板
  平台: Roblox Studio | 语言: Luau
  
  包含:
    - 类型安全的 RemoteEvent/RemoteFunction 封装
    - 服务端输入验证（安全边界）
    - 速率限制（防刷）
    - 可靠的 DataStore 操作（带重试）
    - 玩家数据管理器
    - 服务端游戏循环模式
    
  使用方式:
    将此文件内容拆分到对应的 Roblox Script/LocalScript 中。
--]]

-- ══════════════════════════════════════════════════════
-- 模块：RemoteManager（放在 ReplicatedStorage/Shared/）
-- ══════════════════════════════════════════════════════
-- shared/RemoteManager.lua
local RemoteManager = {}

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService        = game:GetService("RunService")

local IS_SERVER = RunService:IsServer()
local IS_CLIENT = RunService:IsClient()

-- 缓存已创建的 Remote 对象
local remotes_folder: Folder
if IS_SERVER then
    remotes_folder = ReplicatedStorage:FindFirstChild("Remotes")
    if not remotes_folder then
        remotes_folder = Instance.new("Folder")
        remotes_folder.Name = "Remotes"
        remotes_folder.Parent = ReplicatedStorage
    end
else
    remotes_folder = ReplicatedStorage:WaitForChild("Remotes", 10)
    assert(remotes_folder, "Remotes folder not found!")
end

--- 获取或创建 RemoteEvent
function RemoteManager.get_event(name: string): RemoteEvent
    local re = remotes_folder:FindFirstChild(name)
    if not re then
        if IS_SERVER then
            re = Instance.new("RemoteEvent")
            re.Name = name
            re.Parent = remotes_folder
        else
            re = remotes_folder:WaitForChild(name, 10)
            assert(re, "RemoteEvent not found: " .. name)
        end
    end
    return re :: RemoteEvent
end

--- 获取或创建 RemoteFunction
function RemoteManager.get_function(name: string): RemoteFunction
    local rf = remotes_folder:FindFirstChild(name)
    if not rf then
        if IS_SERVER then
            rf = Instance.new("RemoteFunction")
            rf.Name = name
            rf.Parent = remotes_folder
        else
            rf = remotes_folder:WaitForChild(name, 10)
            assert(rf, "RemoteFunction not found: " .. name)
        end
    end
    return rf :: RemoteFunction
end

-- ══════════════════════════════════════════════════════
-- 模块：RateLimiter（服务端使用）
-- ══════════════════════════════════════════════════════
type RateLimiterConfig = {
    max_per_second: number,
    burst: number,
}

local RateLimiter = {}
RateLimiter.__index = RateLimiter

function RateLimiter.new(config: RateLimiterConfig)
    return setmetatable({
        _config  = config,
        _buckets = {} :: {[Player]: {tokens: number, last_refill: number}},
    }, RateLimiter)
end

function RateLimiter:check(player: Player): boolean
    local now = os.clock()
    local bucket = self._buckets[player]
    
    if not bucket then
        self._buckets[player] = {
            tokens = self._config.burst,
            last_refill = now,
        }
        bucket = self._buckets[player]
    end
    
    -- 令牌桶算法：补充令牌
    local elapsed = now - bucket.last_refill
    bucket.tokens = math.min(
        self._config.burst,
        bucket.tokens + elapsed * self._config.max_per_second
    )
    bucket.last_refill = now
    
    -- 消耗令牌
    if bucket.tokens >= 1 then
        bucket.tokens = bucket.tokens - 1
        return true  -- 允许
    end
    return false  -- 限流
end

function RateLimiter:cleanup(player: Player)
    self._buckets[player] = nil
end

-- ══════════════════════════════════════════════════════
-- 模块：PlayerDataManager（服务端）
-- ══════════════════════════════════════════════════════

type PlayerStats = {
    kills: number,
    deaths: number,
    score: number,
}

type PlayerSaveData = {
    version: number,
    coins: number,
    level: number,
    xp: number,
    stats: PlayerStats,
    inventory: {string},
    settings: {[string]: any},
}

local DataStoreService = game:GetService("DataStoreService")
local Players          = game:GetService("Players")

local SAVE_VERSION = 1
local SAVE_KEY_PREFIX = "Player_v" .. SAVE_VERSION .. "_"
local AUTOSAVE_INTERVAL = 60  -- 秒
local MAX_RETRIES = 3

local player_data_store = DataStoreService:GetDataStore("PlayerData")

local PlayerDataManager = {}
local _loaded_data: {[Player]: PlayerSaveData} = {}

local function default_data(): PlayerSaveData
    return {
        version   = SAVE_VERSION,
        coins     = 0,
        level     = 1,
        xp        = 0,
        stats     = {kills=0, deaths=0, score=0},
        inventory = {},
        settings  = {},
    }
end

--- 带重试的 DataStore 操作
local function safe_ds_call(fn: () -> any, retries: number?): (boolean, any)
    retries = retries or MAX_RETRIES
    for attempt = 1, retries do
        local ok, result = pcall(fn)
        if ok then
            return true, result
        else
            warn(string.format("[DataStore] Attempt %d/%d failed: %s", 
                attempt, retries, tostring(result)))
            if attempt < retries then
                task.wait(2 ^ attempt)  -- 指数退避
            end
        end
    end
    return false, nil
end

--- 加载玩家数据
function PlayerDataManager.load(player: Player): PlayerSaveData
    local key = SAVE_KEY_PREFIX .. player.UserId
    
    local ok, data = safe_ds_call(function()
        return player_data_store:GetAsync(key)
    end)
    
    local save_data: PlayerSaveData
    if ok and data then
        -- 数据迁移（版本升级时）
        save_data = data
        if save_data.version ~= SAVE_VERSION then
            save_data = PlayerDataManager._migrate(save_data)
        end
    else
        save_data = default_data()
        if not ok then
            warn("[DataStore] Failed to load data for " .. player.Name .. ", using defaults")
        end
    end
    
    _loaded_data[player] = save_data
    return save_data
end

--- 保存玩家数据
function PlayerDataManager.save(player: Player): boolean
    local data = _loaded_data[player]
    if not data then return false end
    
    local key = SAVE_KEY_PREFIX .. player.UserId
    local ok = safe_ds_call(function()
        player_data_store:SetAsync(key, data)
    end)
    
    if ok then
        print("[DataStore] Saved data for " .. player.Name)
    end
    return ok
end

--- 原子更新（防止并发覆盖）
function PlayerDataManager.update(player: Player, fn: (PlayerSaveData) -> PlayerSaveData)
    local key = SAVE_KEY_PREFIX .. player.UserId
    safe_ds_call(function()
        player_data_store:UpdateAsync(key, function(old_data)
            old_data = old_data or default_data()
            return fn(old_data)
        end)
    end)
end

--- 获取内存中的数据（不读 DataStore）
function PlayerDataManager.get(player: Player): PlayerSaveData?
    return _loaded_data[player]
end

--- 数据迁移
function PlayerDataManager._migrate(data: any): PlayerSaveData
    local migrated = default_data()
    -- 迁移旧字段...
    if data.gold then migrated.coins = data.gold end
    migrated.version = SAVE_VERSION
    return migrated
end

function PlayerDataManager.cleanup(player: Player)
    _loaded_data[player] = nil
end

-- ══════════════════════════════════════════════════════
-- 服务端主脚本（ServerScriptService/GameServer.lua）
-- ══════════════════════════════════════════════════════

-- 定义 Remote 名称常量（服务端+客户端共享）
local REMOTES = {
    PLAYER_ACTION  = "PlayerAction",   -- Client → Server
    DAMAGE_ENTITY  = "DamageEntity",   -- Client → Server
    SYNC_STATE     = "SyncState",      -- Server → Client
    SHOW_UI        = "ShowUI",         -- Server → Client
    GET_LEADERBOARD = "GetLeaderboard", -- Client ↔ Server (Function)
}

-- 初始化 Remotes
local action_event    = RemoteManager.get_event(REMOTES.PLAYER_ACTION)
local damage_event    = RemoteManager.get_event(REMOTES.DAMAGE_ENTITY)
local sync_event      = RemoteManager.get_event(REMOTES.SYNC_STATE)
local leaderboard_fn  = RemoteManager.get_function(REMOTES.GET_LEADERBOARD)

-- 速率限制器
local action_limiter = RateLimiter.new({max_per_second=10, burst=20})
local damage_limiter = RateLimiter.new({max_per_second=5,  burst=10})

-- ── 玩家加入/离开 ──────────────────────────────────
Players.PlayerAdded:Connect(function(player: Player)
    -- 等待角色加载
    local data = PlayerDataManager.load(player)
    print(player.Name .. " loaded. Level:", data.level)
    
    -- 角色生成回调
    player.CharacterAdded:Connect(function(character)
        local humanoid = character:WaitForChild("Humanoid")
        humanoid.Died:Connect(function()
            local d = PlayerDataManager.get(player)
            if d then
                d.stats.deaths = d.stats.deaths + 1
            end
        end)
    end)
    
    -- 发送初始状态给客户端
    sync_event:FireClient(player, {
        type    = "init",
        level   = data.level,
        coins   = data.coins,
        inventory = data.inventory,
    })
end)

Players.PlayerRemoving:Connect(function(player: Player)
    -- 同步保存（玩家离线前）
    PlayerDataManager.save(player)
    PlayerDataManager.cleanup(player)
    action_limiter:cleanup(player)
    damage_limiter:cleanup(player)
end)

-- 服务端关闭保存
game:BindToClose(function()
    for _, player in ipairs(Players:GetPlayers()) do
        PlayerDataManager.save(player)
    end
end)

-- ── 处理客户端动作 ─────────────────────────────────
action_event.OnServerEvent:Connect(function(player: Player, action_type: string, payload: any)
    -- 1. 速率限制
    if not action_limiter:check(player) then
        warn("[Security] Rate limit hit: " .. player.Name .. " action=" .. action_type)
        return
    end
    
    -- 2. 类型验证（永远不信任客户端）
    if typeof(action_type) ~= "string" then return end
    
    -- 3. 处理动作
    if action_type == "buy_item" then
        if typeof(payload) ~= "table" then return end
        local item_id = payload.item_id
        if typeof(item_id) ~= "string" then return end
        
        local data = PlayerDataManager.get(player)
        if not data then return end
        
        -- 物品价格表（服务端权威数据，不相信客户端传来的价格）
        local SHOP_PRICES = {sword=100, shield=80, potion=20}
        local price = SHOP_PRICES[item_id]
        if not price then return end
        
        if data.coins >= price then
            data.coins = data.coins - price
            data.inventory[#data.inventory + 1] = item_id
            
            -- 通知客户端更新
            sync_event:FireClient(player, {
                type = "purchase_success",
                item = item_id,
                coins = data.coins,
            })
        else
            sync_event:FireClient(player, {
                type = "purchase_fail",
                reason = "insufficient_coins",
            })
        end
    end
end)

-- ── RemoteFunction：排行榜 ─────────────────────────
leaderboard_fn.OnServerInvoke = function(player: Player, request: any)
    -- 返回顶10玩家数据（示例）
    return {
        {rank=1, name="Player1", score=9999},
        {rank=2, name="Player2", score=8888},
    }
end

-- ── 自动保存 ───────────────────────────────────────
task.spawn(function()
    while true do
        task.wait(AUTOSAVE_INTERVAL)
        for _, player in ipairs(Players:GetPlayers()) do
            PlayerDataManager.save(player)
        end
    end
end)

-- ══════════════════════════════════════════════════════
-- 客户端脚本（StarterPlayerScripts/GameClient.lua）
-- ══════════════════════════════════════════════════════
--[[
local Players    = game:GetService("Players")
local LocalPlayer = Players.LocalPlayer
local remotes_folder = game:GetService("ReplicatedStorage"):WaitForChild("Remotes")

local sync_event   = remotes_folder:WaitForChild("SyncState")
local action_event = remotes_folder:WaitForChild("PlayerAction")

-- 本地状态
local local_state = {
    coins = 0,
    level = 1,
    inventory = {},
}

-- 接收服务端同步
sync_event.OnClientEvent:Connect(function(data)
    if data.type == "init" then
        local_state.coins = data.coins
        local_state.level = data.level
        local_state.inventory = data.inventory
        -- 更新 UI...
        
    elseif data.type == "purchase_success" then
        local_state.coins = data.coins
        table.insert(local_state.inventory, data.item)
        -- 显示购买成功提示...
        
    elseif data.type == "purchase_fail" then
        -- 显示失败提示...
    end
end)

-- 发送购买请求
local function buy_item(item_id)
    action_event:FireServer("buy_item", {item_id = item_id})
end
--]]
