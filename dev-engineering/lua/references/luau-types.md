# Luau 类型系统与 Roblox API 参考

## Luau 类型注解

```lua
-- 基础类型
local x: number = 42
local s: string = "hello"
local b: boolean = true
local n: nil = nil

-- 可选（联合 nil）
local maybe: string? = nil

-- 函数类型
local fn: (number, string) -> boolean

-- 泛型
type Array<T> = {[number]: T}
type Dict<K, V> = {[K]: V}
type Map<V> = Dict<string, V>

-- 联合类型
type StringOrNum = string | number
type State = "idle" | "run" | "jump" | "dead"

-- 交叉类型（组合）
type Named = {name: string}
type Positioned = {x: number, y: number}
type NamedEntity = Named & Positioned

-- 复杂类型
type PlayerData = {
    userId: number,
    username: string,
    level: number,
    stats: {
        kills: number,
        deaths: number,
    },
    inventory: Array<string>,
}

-- 泛型函数
local function first<T>(arr: {T}): T?
    return arr[1]
end

-- 类型断言
local x = getValue() :: string

-- typeof 类型推断（运行时）
local t = typeof(x)  -- "string", "number", "boolean", "table", etc.
-- 注意：Roblox 用 typeof 而非 type()，因为 type(Vector3.new()) == "userdata"
-- 而 typeof(Vector3.new()) == "Vector3"
```

## Roblox 内建类型

```lua
-- 值类型（无 GC 压力）
local v3: Vector3     = Vector3.new(1, 2, 3)
local v2: Vector2     = Vector2.new(10, 20)
local cf: CFrame      = CFrame.new(0, 5, 0) * CFrame.Angles(0, math.pi, 0)
local c:  Color3      = Color3.fromRGB(255, 128, 0)
local ud: UDim2       = UDim2.new(0.5, 0, 0.5, 0)  -- 相对+绝对
local ud1: UDim       = UDim.new(0.5, 10)
local rect: Rect      = Rect.new(0, 0, 100, 100)
local r:  Ray         = Ray.new(origin, direction)

-- Vector3 操作
local pos = Vector3.new(1, 0, 0)
local sum = pos + Vector3.new(0, 1, 0)     -- (1,1,0)
local scaled = pos * 5                      -- (5,0,0)
local dist = pos:Dot(other)                 -- 点积
local cross = pos:Cross(other)              -- 叉积
local unit = pos.Unit                        -- 单位向量
local mag = pos.Magnitude                    -- 长度
local lerped = pos:Lerp(target, 0.1)        -- 线性插值

-- CFrame 操作
local cf = CFrame.new(x, y, z)
local rotated = CFrame.new(0,0,0) * CFrame.Angles(rx, ry, rz)
local lookAt = CFrame.lookAt(from, to)
local pos, right, up, back = cf:GetComponents()
local x, y, z = cf.X, cf.Y, cf.Z           -- 位置分量
local rx, ry, rz = cf:ToEulerAnglesXYZ()   -- 欧拉角
local combined = cf1 * cf2                   -- 复合变换
local local_cf = cf:ToObjectSpace(world_cf)  -- 世界→本地
local world_cf = cf:ToWorldSpace(local_cf)  -- 本地→世界
```

## Roblox 常用 API

```lua
-- Instance 操作
local part = Instance.new("Part")
part.Name = "MyPart"
part.Parent = workspace
part.Anchored = true
part.Size = Vector3.new(4, 1, 4)
part.Position = Vector3.new(0, 5, 0)
part.CFrame = CFrame.new(0, 5, 0)
part.Color = Color3.fromRGB(255, 0, 0)
part.Material = Enum.Material.SmoothPlastic
part.Transparency = 0.5
part.CanCollide = true
part.Massless = false

-- 查找子级
local child = parent:FindFirstChild("ChildName")
local child = parent:FindFirstChild("ChildName", true)  -- 递归
local typed = parent:FindFirstChildOfClass("Model")
local typed = parent:FindFirstChildWhichIsA("BasePart")  -- 包含子类
local children = parent:GetChildren()
local descendants = parent:GetDescendants()
local found = parent:WaitForChild("Name", timeout)  -- 等待直到出现

-- 实例事件
part.ChildAdded:Connect(function(child) end)
part.ChildRemoved:Connect(function(child) end)
part.AncestryChanged:Connect(function(child, parent) end)
part:GetPropertyChangedSignal("Transparency"):Connect(function() end)

-- 克隆与销毁
local clone = instance:Clone()
clone.Parent = workspace
instance:Destroy()

-- TweenService 动画
local TweenService = game:GetService("TweenService")
local info = TweenInfo.new(
    1.0,                      -- 时长
    Enum.EasingStyle.Quad,    -- 缓动类型
    Enum.EasingDirection.Out, -- 方向
    0,                        -- 重复次数（-1=无限）
    false,                    -- 反向
    0                         -- 延迟
)
local tween = TweenService:Create(part, info, {
    Position = Vector3.new(0, 10, 0),
    Transparency = 0.5
})
tween:Play()
tween.Completed:Connect(function(state)
    if state == Enum.PlaybackState.Completed then
        print("Done!")
    end
end)

-- 射线检测
local rayOrigin = Vector3.new(0, 100, 0)
local rayDirection = Vector3.new(0, -200, 0)

local raycastParams = RaycastParams.new()
raycastParams.FilterDescendantsInstances = {character}
raycastParams.FilterType = Enum.RaycastFilterType.Exclude

local result = workspace:Raycast(rayOrigin, rayDirection, raycastParams)
if result then
    print("Hit:", result.Instance.Name)
    print("Position:", result.Position)
    print("Normal:", result.Normal)
    print("Material:", result.Material)
end

-- 玩家角色
local Players = game:GetService("Players")
local player = Players.LocalPlayer  -- 仅客户端
local character = player.Character or player.CharacterAdded:Wait()
local humanoid = character:WaitForChild("Humanoid")
local rootPart = character:WaitForChild("HumanoidRootPart")

humanoid.Health = 100
humanoid.MaxHealth = 100
humanoid:TakeDamage(25)
humanoid.Died:Connect(function() print("Player died") end)
humanoid:MoveTo(Vector3.new(0, 0, 0))

-- GUI
local screenGui = Instance.new("ScreenGui")
screenGui.Parent = player.PlayerGui

local frame = Instance.new("Frame")
frame.Size = UDim2.new(0, 200, 0, 100)
frame.Position = UDim2.new(0.5, -100, 0.5, -50)
frame.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
frame.Parent = screenGui

local button = Instance.new("TextButton")
button.Size = UDim2.new(1, 0, 0, 40)
button.Text = "Click Me"
button.MouseButton1Click:Connect(function()
    print("Clicked!")
end)
button.Parent = frame

-- 运行时循环
local RunService = game:GetService("RunService")

-- Heartbeat（物理后，每帧）
RunService.Heartbeat:Connect(function(dt)
    -- 游戏逻辑
end)

-- RenderStepped（渲染前，仅客户端）
RunService.RenderStepped:Connect(function(dt)
    -- 视觉更新（摄像机等）
end)

-- Stepped（物理前）
RunService.Stepped:Connect(function(time, dt)
    -- 物理前处理
end)
```

## Luau 性能技巧

```lua
-- 1. 使用 buffer（Luau 特有，高性能二进制数据）
local buf = buffer.create(1024)
buffer.writei32(buf, 0, 42)
local val = buffer.readi32(buf, 0)  -- 42

-- 2. 类型注解帮助 Luau 优化
-- 有注解的数字运算比无注解快约 2-3x

-- 3. table.freeze（只读表，可被优化）
local CONSTANTS = table.freeze({
    MAX_SPEED = 200,
    GRAVITY = -50,
    JUMP_FORCE = 80,
})

-- 4. 避免 pairs() 在热路径（用 ipairs 或数字索引）
-- 5. 使用 task 库替代 wait()
local task = game:GetService("TaskScheduler") -- Roblox

task.wait(1)                    -- 等待（替代 wait()）
task.spawn(fn, args)            -- 立即执行（下一帧）
task.defer(fn, args)            -- 延迟到帧末尾
task.delay(seconds, fn, args)   -- 延迟执行
task.cancel(thread)             -- 取消
```
