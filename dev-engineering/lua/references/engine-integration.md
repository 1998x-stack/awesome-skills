# 游戏引擎集成参考

## 目录
- [LÖVE2D](#löve2d)
- [Roblox / Luau](#roblox--luau)
- [Defold](#defold)
- [Unity (MoonSharp/NLua)](#unity-moonsharpnlua)
- [CryEngine / Lumberyard](#cryengine--lumberyard)
- [Cocos2d-x](#cocos2d-x)
- [Corona SDK / Solar2D](#corona-sdk--solar2d)
- [自定义 C++ 引擎](#自定义-c-引擎)

---

## LÖVE2D

**版本**: LÖVE 11.x | **Lua**: 5.1 (JIT) | **平台**: Windows/macOS/Linux/Android/iOS

### 生命周期回调

```lua
love.load()           -- 游戏初始化（一次）
love.update(dt)       -- 逻辑更新（每帧）
love.draw()           -- 渲染（每帧，在 update 后）
love.quit()           -- 退出前（返回 true 可取消退出）
love.resize(w, h)     -- 窗口大小变化
love.focus(f)         -- 窗口焦点变化
love.keypressed(key, scancode, isrepeat)
love.keyreleased(key, scancode)
love.mousepressed(x, y, button, istouch, presses)
love.mousereleased(x, y, button, istouch, presses)
love.mousemoved(x, y, dx, dy, istouch)
love.wheelmoved(x, y)
love.touchpressed(id, x, y, dx, dy, pressure)
love.touchreleased(id, x, y, dx, dy, pressure)
love.gamepadpressed(joystick, button)
love.gamepadreleased(joystick, button)
love.joystickaxis(joystick, axis, value)
love.errhand(msg)     -- 全局错误处理
```

### 核心模块速查

```lua
-- 图形
love.graphics.setColor(r, g, b, a)
love.graphics.clear(r, g, b, a)
love.graphics.rectangle(mode, x, y, w, h, rx, ry)  -- mode: "fill"/"line"
love.graphics.circle(mode, x, y, radius)
love.graphics.line(x1, y1, x2, y2, ...)
love.graphics.print(text, x, y, r, sx, sy, ox, oy)
love.graphics.draw(drawable, x, y, r, sx, sy, ox, oy)
love.graphics.push()           -- 保存变换矩阵
love.graphics.pop()            -- 恢复变换矩阵
love.graphics.translate(x, y)
love.graphics.rotate(angle)
love.graphics.scale(sx, sy)
love.graphics.setShader(shader)
love.graphics.setBlendMode(mode, alphamode)
love.graphics.newCanvas(w, h)
love.graphics.setCanvas(canvas) -- nil 恢复默认

-- 资源加载
love.graphics.newImage(path)
love.graphics.newFont(path, size)
love.graphics.newShader(vert, frag)
love.graphics.newSpriteBatch(image, maxsprites)
love.audio.newSource(path, type)  -- type: "static"/"stream"
love.graphics.newQuad(x, y, w, h, iw, ih)  -- Spritesheet

-- 物理（Box2D）
local world = love.physics.newWorld(gx, gy, sleep)
local body = love.physics.newBody(world, x, y, type)  -- "static"/"dynamic"/"kinematic"
local shape = love.physics.newRectangleShape(w, h)
local fixture = love.physics.newFixture(body, shape, density)
fixture:setFriction(f)
fixture:setRestitution(r)
fixture:setCategory(cat)
fixture:setMask(mask)
world:setCallbacks(beginContact, endContact, preSolve, postSolve)

-- 输入
love.keyboard.isDown("space", "left")
love.mouse.getPosition()
love.mouse.isDown(1)  -- 1=左键, 2=右键, 3=中键
love.gamepad:isGamepadDown("a")
```

### 完整项目结构

```
my_game/
├── main.lua          -- 入口（love.load/update/draw）
├── conf.lua          -- 配置（love.conf）
├── src/
│   ├── game.lua      -- 游戏状态管理
│   ├── player.lua    -- 玩家
│   ├── enemy.lua     -- 敌人
│   └── ui.lua        -- 界面
├── assets/
│   ├── sprites/
│   ├── sounds/
│   └── fonts/
└── libs/
    ├── class.lua
    └── vector.lua
```

```lua
-- conf.lua
function love.conf(t)
    t.title = "My Game"
    t.version = "11.4"
    t.window.width = 1280
    t.window.height = 720
    t.window.resizable = true
    t.window.vsync = 1
    t.window.msaa = 4
    t.modules.joystick = true
    t.modules.physics = true
    t.console = false  -- Windows 控制台
end
```

---

## Roblox / Luau

**Lua版本**: Luau (Lua 5.1 超集) | **平台**: Roblox Studio

### 服务架构

```
DataModel (game)
├── Workspace                    -- 3D 场景，客户端+服务端可见
│   └── [Parts, Models, Scripts]
├── ServerScriptService          -- 仅服务端执行，客户端不可见
│   └── Script.lua (type=Script)
├── ServerStorage               -- 服务端私有存储
├── ReplicatedStorage           -- 服务端+客户端共享（只读数据）
│   └── RemoteEvents/
├── ReplicatedFirst             -- 客户端第一个复制（加载画面）
├── StarterPlayer
│   ├── StarterPlayerScripts    -- 每个玩家本地执行
│   │   └── LocalScript.lua
│   └── StarterCharacterScripts -- 角色生成时执行
├── StarterGui                  -- 客户端 UI
├── Lighting                    -- 环境光
├── SoundService               -- 音效
└── Teams
```

### 服务引用

```lua
-- 常用服务
local Players         = game:GetService("Players")
local RunService      = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local TweenService    = game:GetService("TweenService")
local DataStoreService = game:GetService("DataStoreService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local HttpService     = game:GetService("HttpService")
local MarketplaceService = game:GetService("MarketplaceService")
local PhysicsService  = game:GetService("PhysicsService")
local CollectionService = game:GetService("CollectionService")
local SoundService    = game:GetService("SoundService")
local Workspace       = game:GetService("Workspace")  -- 等价于 workspace

-- 检查运行环境
RunService:IsServer()   -- 是否在服务端
RunService:IsClient()   -- 是否在客户端
RunService:IsStudio()   -- 是否在 Studio 中
```

### 远程通信

```lua
-- RemoteEvent（单向，不等待响应）
local re = Instance.new("RemoteEvent")
re.Name = "MyEvent"
re.Parent = ReplicatedStorage

-- 服务端 → 客户端
re:FireClient(player, data1, data2)
re:FireAllClients(data1, data2)

-- 客户端 → 服务端
re:FireServer(data1, data2)

-- 监听
re.OnServerEvent:Connect(function(player, data1, data2) end)
re.OnClientEvent:Connect(function(data1, data2) end)

-- RemoteFunction（双向，等待返回值）
local rf = Instance.new("RemoteFunction")
rf.Name = "MyFunction"
rf.Parent = ReplicatedStorage

-- 服务端实现
rf.OnServerInvoke = function(player, request)
    -- 处理请求
    return {success = true, data = "result"}
end

-- 客户端调用（阻塞直到服务端返回）
local result = rf:InvokeServer(requestData)
print(result.data)
```

### DataStore 持久化

```lua
-- 服务端脚本
local DataStoreService = game:GetService("DataStoreService")
local playerDataStore = DataStoreService:GetDataStore("PlayerData_v1")

local function savePlayerData(player, data)
    local key = "Player_" .. player.UserId
    local success, err = pcall(function()
        playerDataStore:SetAsync(key, data)
    end)
    if not success then
        warn("Save failed for " .. player.Name .. ": " .. err)
    end
end

local function loadPlayerData(player)
    local key = "Player_" .. player.UserId
    local success, data = pcall(function()
        return playerDataStore:GetAsync(key)
    end)
    if success then
        return data or {coins=0, level=1}
    else
        warn("Load failed: " .. tostring(data))
        return {coins=0, level=1}
    end
end

-- 使用 UpdateAsync 原子操作
playerDataStore:UpdateAsync(key, function(oldData)
    oldData = oldData or {coins=0}
    oldData.coins = oldData.coins + 100
    return oldData
end)
```

---

## Defold

**Lua版本**: Lua 5.1 | **平台**: 全平台（含 Web）

### 脚本组件生命周期

```lua
function init(self)      end  -- 首帧前
function final(self)     end  -- 销毁前
function update(self, dt) end -- 每帧
function fixed_update(self, dt) end -- 固定时间步
function on_message(self, message_id, message, sender) end
function on_input(self, action_id, action) end
function on_reload(self) end  -- 热重载时
```

### 消息传递

```lua
-- 消息 ID 是 hash 值（编译期优化）
local MSG_DAMAGE = hash("damage")
local MSG_HEAL   = hash("heal")

-- 发送消息
msg.post("player#health", MSG_DAMAGE, {amount = 25})
msg.post(".", "disable")                    -- 发给自己的组件
msg.post("../enemy", "alert")               -- 发给父级的 enemy GO
msg.post("/game_manager#controller", "level_complete")  -- 绝对路径

-- 接收消息
function on_message(self, message_id, message, sender)
    if message_id == MSG_DAMAGE then
        self.hp = self.hp - message.amount
        if self.hp <= 0 then
            msg.post(".", "set_enabled", {enabled = false})
            msg.post("/game_manager", "player_died")
        end
    elseif message_id == hash("collision_response") then
        -- 物理碰撞
        print("Collided with:", message.other_id)
    end
end
```

### 游戏对象操作

```lua
-- 位置/旋转/缩放
local pos = go.get_position()                 -- 本地空间
local wpos = go.get_world_position()          -- 世界空间
go.set_position(vmath.vector3(x, y, 0))
go.set_rotation(vmath.quat_rotation_z(angle))

-- 创建/销毁
local id = factory.create("#enemy_factory", pos, rot, props, scale)
go.delete(id)
go.delete_all()  -- 删除所有 factory 创建的对象

-- 动画
local url = msg.url("#sprite")
sprite.play_flipbook(url, hash("run"))

-- 属性系统
local color = go.get("#sprite", "tint")
go.set("#sprite", "tint", vmath.vector4(1, 0, 0, 1))  -- 红色
go.animate("#sprite", "tint", go.PLAYBACK_ONCE_FORWARD,
    vmath.vector4(1, 1, 1, 1), go.EASING_OUTSINE, 0.5)  -- 动画

-- 输入映射
function on_input(self, action_id, action)
    if action_id == hash("jump") then
        if action.pressed then  -- 仅按下瞬间
            self.velocity.y = JUMP_FORCE
        end
    end
    if action_id == hash("move_right") then
        -- action.value: 0.0 ~ 1.0（模拟输入）
        self.velocity.x = action.value * SPEED
    end
end
```

---

## Unity (MoonSharp/NLua)

### MoonSharp 集成

```csharp
// 安装: NuGet > MoonSharp.Interpreter

using MoonSharp.Interpreter;

// 1. 注册 C# 类型
[MoonSharpUserData]
public class Transform2D {
    public float X { get; set; }
    public float Y { get; set; }
    public void Translate(float dx, float dy) { X += dx; Y += dy; }
}

// 2. 自动注册程序集所有标记类型
UserData.RegisterAssembly();

// 3. 创建脚本
var script = new Script();

// 4. 注入对象
script.Globals["transform"] = myTransform;
script.Globals["Time"] = UserData.Create(typeof(Time));  // 静态类

// 5. 注入 C# 函数
script.Globals["log"] = (Action<string>)Debug.Log;
script.Globals["lerp"] = (Func<float, float, float, float>)Mathf.Lerp;

// 6. 执行
script.DoString("transform:Translate(10, 0)");
script.DoFile("Assets/Scripts/Lua/behavior.lua");

// 7. 调用 Lua 函数
DynValue fn = script.Globals.Get("update");
script.Call(fn, Time.deltaTime);

// 8. 获取返回值
DynValue result = script.DoString("return 1 + 2");
float val = (float)result.Number;  // 3.0
```

### NLua 集成（基于 KeraLua/原生 Lua）

```csharp
using NLua;

var lua = new Lua();

// 注册 C# 对象
lua["myObj"] = new MyClass();

// 注册函数
lua.RegisterFunction("log", typeof(Debug).GetMethod("Log", 
    new Type[]{ typeof(object) }));

// 执行
lua.DoString("myObj:Method()");

// 获取全局变量
var result = lua["my_variable"];
var table = lua.GetTable("my_table");
```

---

## CryEngine / Lumberyard

```lua
-- 实体脚本基本结构
MyEntity = {
    Properties = {
        -- 编辑器属性（类型通过值推断）
        bEnabled = 1,           -- bool
        fSpeed = 5.0,           -- float
        nMaxCount = 10,         -- int
        sName = "default",      -- string
        
        -- 嵌套属性组
        Attack = {
            fDamage = 25.0,
            fRange = 5.0,
        },
    },
}

function MyEntity:OnInit()
    self:OnReset()
end

function MyEntity:OnReset()
    self.speed = self.Properties.fSpeed
end

function MyEntity:OnUpdate(dt)
    if self.Properties.bEnabled == 1 then
        -- 移动
        local pos = self:GetWorldPos()
        pos.y = pos.y + self.speed * dt
        self:SetWorldPos(pos)
    end
end

function MyEntity:OnCollision(hit)
    -- hit.pos, hit.normal, hit.damage
end

function MyEntity:Event_OnActivate()
    self.Properties.bEnabled = 1
end

-- Flow Graph 节点
function MyEntity:OnFlowgraphActivation(nodeID, inputs)
end

-- AI 脚本系统
function MyEntity:SetupState(stateMachine)
    stateMachine:SetDefaultState("Idle")
    stateMachine:AddState{
        name = "Idle",
        OnEnter = function(self)
            AI.SetBehaviorVariable(self.id, "IsAlert", false)
        end,
        transitions = {
            {to = "Alert", condition = function(self)
                return AI.GetBehaviorVariable(self.id, "ThreatDetected")
            end}
        }
    }
end
```

---

## Cocos2d-x

```lua
-- Cocos2d-x Lua Binding

-- 场景与层
local scene = cc.Scene:create()
local layer = cc.Layer:create()
scene:addChild(layer, 0, "main_layer")

-- 精灵
local sprite = cc.Sprite:create("res/hero.png")
sprite:setPosition(cc.p(240, 160))
sprite:setAnchorPoint(cc.p(0.5, 0.5))
layer:addChild(sprite, 1, "hero")

-- 动作
local moveTo   = cc.MoveTo:create(1.0, cc.p(300, 200))
local moveBy   = cc.MoveBy:create(1.0, cc.p(50, 0))
local scaleTo  = cc.ScaleTo:create(0.5, 1.5)
local rotateTo = cc.RotateTo:create(0.5, 45)
local fadeIn   = cc.FadeIn:create(0.5)
local fadeOut  = cc.FadeOut:create(0.5)
local seq      = cc.Sequence:create(moveTo, moveBy)
local spawn    = cc.Spawn:create(scaleTo, rotateTo)
local repeat_  = cc.Repeat:create(seq, 3)
local forever  = cc.RepeatForever:create(forever_action)

sprite:runAction(seq)
sprite:stopAllActions()

-- 动画（帧动画）
local animation = cc.Animation:create()
for i = 1, 8 do
    animation:addSpriteFrameWithFile(string.format("run_%02d.png", i))
end
animation:setDelayPerUnit(1/12)  -- 12 fps
animation:setRestoreOriginalFrame(true)
local animate = cc.Animate:create(animation)
sprite:runAction(cc.RepeatForever:create(animate))

-- 事件系统
local listener = cc.EventListenerTouchOneByOne:create()
listener:setSwallowTouches(true)
listener:registerScriptHandler(function(touch, event)
    return true  -- 消费事件
end, cc.Handler.EVENT_TOUCH_BEGAN)
listener:registerScriptHandler(function(touch, event)
end, cc.Handler.EVENT_TOUCH_ENDED)

cc.Director:getInstance():getEventDispatcher()
    :addEventListenerWithSceneGraphPriority(listener, sprite)

-- 物理
local physicsWorld = scene:getPhysicsWorld()
physicsWorld:setGravity(cc.p(0, -300))
physicsWorld:setDebugDrawMask(cc.PhysicsWorld.DEBUGDRAW_ALL)

local body = cc.PhysicsBody:createBox(cc.size(50, 50),
    cc.PhysicsMaterial(1.0, 0.5, 0.5))
sprite:setPhysicsBody(body)

-- 联系监听
local contactListener = cc.EventListenerPhysicsContact:create()
contactListener:registerScriptHandler(function(contact)
    local a = contact:getShapeA():getBody():getNode()
    local b = contact:getShapeB():getBody():getNode()
end, cc.Handler.EVENT_PHYSICS_CONTACT_BEGIN)
```

---

## Corona SDK / Solar2D

```lua
-- Solar2D 完整游戏结构

local physics = require("physics")
physics.start()
physics.setGravity(0, 9.8)
-- physics.setDrawMode("hybrid")  -- 调试

-- 显示组（管理场景对象）
local scene = display.newGroup()

-- 物理对象
local ground = display.newRect(scene, cx, display.contentHeight - 25, 
                               display.contentWidth, 50)
physics.addBody(ground, "static", {
    friction = 0.5,
    bounce = 0.1
})

-- 多边形物理体
local verts = {-20, -20, 20, -20, 20, 20, -20, 20}
physics.addBody(obj, "dynamic", {
    shape = verts,
    density = 1.0,
    friction = 0.3,
    bounce = 0.5
})

-- 关节
local joint = physics.newJoint("pivot", bodyA, bodyB, anchorX, anchorY)
joint:setRotationLimits(-90, 90)

-- 事件
Runtime:addEventListener("enterFrame", function(e)
    -- e.time: 毫秒, e.frame: 帧号
end)

obj:addEventListener("touch", function(e)
    -- e.phase: "began"/"moved"/"ended"/"cancelled"
    -- e.x, e.y: 触摸坐标
    return true
end)

-- Composer（场景管理）
local composer = require("composer")
composer.gotoScene("scenes.game", {
    effect = "fade",
    time = 500,
    params = {level = 1}
})

-- scenes/game.lua
local composer = require("composer")
local scene = composer.newScene()

function scene:create(event)
    local sceneGroup = self.view
    -- 创建场景内容（尚未显示）
end

function scene:show(event)
    if event.phase == "will" then
        -- 即将显示
    elseif event.phase == "did" then
        -- 已显示，启动逻辑
        local params = event.params  -- {level = 1}
    end
end

function scene:hide(event)
    if event.phase == "will" then
        -- 即将隐藏，停止逻辑
    end
end

function scene:destroy(event)
    -- 清理资源
end

scene:addEventListener("create", scene)
scene:addEventListener("show", scene)
scene:addEventListener("hide", scene)
scene:addEventListener("destroy", scene)

return scene
```

---

## 自定义 C++ 引擎

### 完整嵌入模板

```cpp
// LuaEngine.h
#pragma once
extern "C" {
#include "lua.h"
#include "lualib.h"
#include "lauxlib.h"
}
#include <string>
#include <functional>
#include <unordered_map>

class LuaEngine {
public:
    lua_State *L;
    
    LuaEngine();
    ~LuaEngine() { if(L) lua_close(L); }
    
    bool LoadFile(const std::string &path);
    bool LoadString(const std::string &code, const std::string &name = "chunk");
    
    // 安全调用（带 traceback）
    bool Call(const std::string &func);
    bool CallDt(const std::string &func, float dt);
    
    // 注册 C 函数
    void Register(const std::string &name, lua_CFunction fn);
    void RegisterModule(const std::string &name, const luaL_Reg *funcs);
    
    // 全局变量操作
    template<typename T> void Set(const std::string &key, T value);
    template<typename T> T Get(const std::string &key, T def = T{});
    
    // 脚本热重载
    bool Reload(const std::string &path);

private:
    static int ErrorHandler(lua_State *L);
    int errHandlerIdx = 0;
};
```

### 引擎 API 设计模式

```c
// 引擎暴露给 Lua 的完整 API 示例

// === Graphics API ===
static int gfx_clear(lua_State *L) {
    float r = luaL_optnumber(L, 1, 0);
    float g = luaL_optnumber(L, 2, 0);
    float b = luaL_optnumber(L, 3, 0);
    float a = luaL_optnumber(L, 4, 1);
    Engine::Graphics::Clear(r, g, b, a);
    return 0;
}

static int gfx_draw_sprite(lua_State *L) {
    int sprite_id = luaL_checkinteger(L, 1);
    float x = luaL_checknumber(L, 2);
    float y = luaL_checknumber(L, 3);
    float rot = luaL_optnumber(L, 4, 0);
    float sx = luaL_optnumber(L, 5, 1);
    float sy = luaL_optnumber(L, 6, 1);
    Engine::Graphics::DrawSprite(sprite_id, x, y, rot, sx, sy);
    return 0;
}

static const luaL_Reg gfx_lib[] = {
    {"clear",       gfx_clear},
    {"draw_sprite", gfx_draw_sprite},
    {"load_image",  gfx_load_image},
    {"new_canvas",  gfx_new_canvas},
    {NULL, NULL}
};

// === 注册所有模块 ===
void LuaEngine::RegisterEngineAPI() {
    struct { const char* name; const luaL_Reg* funcs; } modules[] = {
        {"Graphics", gfx_lib},
        {"Input",    input_lib},
        {"Audio",    audio_lib},
        {"Physics",  physics_lib},
        {"Entity",   entity_lib},
        {"Scene",    scene_lib},
    };
    for (auto &m : modules) {
        luaL_newlib(L, m.funcs);
        lua_setglobal(L, m.name);
    }
}
```
