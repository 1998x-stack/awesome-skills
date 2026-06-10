--[[
  love2d_starter.lua — LÖVE2D 完整游戏模板
  引擎: LÖVE 11.x  |  Lua: LuaJIT (5.1 兼容)
  
  功能:
    - 场景管理（SceneManager）
    - 输入管理（按键/鼠标/手柄）
    - 资源缓存（图片/字体/音效）
    - 摄像机系统（跟随、震动、缩放）
    - 游戏对象基类
    - 调试模式（FPS、物理形状）

  文件结构:
    main.lua        ← 这个文件
    conf.lua        ← LÖVE 配置
    src/
      scenes/
        game.lua
        menu.lua
      entities/
        player.lua
      libs/
        camera.lua
--]]

-- ══════════════════════════════════════════════════════
-- conf.lua 内容（单独文件）
-- function love.conf(t)
--     t.title   = "My Game"
--     t.version = "11.4"
--     t.window.width  = 1280
--     t.window.height = 720
--     t.window.resizable = true
--     t.window.vsync  = 1
--     t.modules.physics = true
--     t.console = false
-- end
-- ══════════════════════════════════════════════════════

-- ────────────────────────────────────────────────────
-- 资源缓存
-- ────────────────────────────────────────────────────
local Assets = {}
Assets._images = {}
Assets._fonts  = {}
Assets._sounds = {}
Assets._quads  = {}

function Assets.image(path)
    if not Assets._images[path] then
        Assets._images[path] = love.graphics.newImage(path)
        Assets._images[path]:setFilter("nearest", "nearest")  -- 像素风格
    end
    return Assets._images[path]
end

function Assets.font(path, size)
    local key = path .. ":" .. size
    if not Assets._fonts[key] then
        if path == "default" then
            Assets._fonts[key] = love.graphics.newFont(size)
        else
            Assets._fonts[key] = love.graphics.newFont(path, size)
        end
    end
    return Assets._fonts[key]
end

function Assets.sound(path, kind)
    if not Assets._sounds[path] then
        Assets._sounds[path] = love.audio.newSource(path, kind or "static")
    end
    return Assets._sounds[path]
end

-- Spritesheet 四边形
function Assets.quad(image, x, y, w, h)
    local key = tostring(image) .. ":" .. x .. "," .. y .. "," .. w .. "," .. h
    if not Assets._quads[key] then
        local iw, ih = image:getDimensions()
        Assets._quads[key] = love.graphics.newQuad(x, y, w, h, iw, ih)
    end
    return Assets._quads[key]
end

-- ────────────────────────────────────────────────────
-- 摄像机
-- ────────────────────────────────────────────────────
local Camera = {}
Camera.__index = Camera

function Camera.new(x, y)
    return setmetatable({
        x = x or 0, y = y or 0,
        zoom = 1,
        rotation = 0,
        _shake_time = 0,
        _shake_power = 0,
        _shake_x = 0,
        _shake_y = 0,
        _target = nil,
        _lerp = 0.1,
    }, Camera)
end

function Camera:follow(target, lerp)
    self._target = target
    self._lerp = lerp or 0.1
end

function Camera:shake(duration, power)
    self._shake_time = duration
    self._shake_power = power or 8
end

function Camera:update(dt)
    -- 跟随目标
    if self._target then
        local tx = self._target.x - love.graphics.getWidth() / 2 / self.zoom
        local ty = self._target.y - love.graphics.getHeight() / 2 / self.zoom
        self.x = self.x + (tx - self.x) * self._lerp
        self.y = self.y + (ty - self.y) * self._lerp
    end
    -- 屏幕震动
    if self._shake_time > 0 then
        self._shake_time = self._shake_time - dt
        local p = self._shake_power * (self._shake_time > 0 and 1 or 0)
        self._shake_x = (math.random() * 2 - 1) * p
        self._shake_y = (math.random() * 2 - 1) * p
    else
        self._shake_x, self._shake_y = 0, 0
    end
end

function Camera:attach()
    love.graphics.push()
    love.graphics.translate(love.graphics.getWidth()/2, love.graphics.getHeight()/2)
    love.graphics.scale(self.zoom, self.zoom)
    love.graphics.rotate(self.rotation)
    love.graphics.translate(-self.x + self._shake_x, -self.y + self._shake_y)
end

function Camera:detach()
    love.graphics.pop()
end

function Camera:to_world(sx, sy)
    local cx = love.graphics.getWidth() / 2
    local cy = love.graphics.getHeight() / 2
    local wx = (sx - cx) / self.zoom + self.x
    local wy = (sy - cy) / self.zoom + self.y
    return wx, wy
end

-- ────────────────────────────────────────────────────
-- 输入管理器
-- ────────────────────────────────────────────────────
local Input = {}
Input._bindings = {}
Input._state = {}
Input._prev  = {}

-- 绑定动作
function Input.bind(action, ...)
    Input._bindings[action] = {...}
end

function Input.update()
    -- 复制当前状态到 prev（用于 pressed/released 检测）
    for k, v in pairs(Input._state) do
        Input._prev[k] = v
    end
end

function Input.is_down(action)
    for _, key in ipairs(Input._bindings[action] or {}) do
        if love.keyboard.isDown(key) then return true end
        if love.mouse.isDown(tonumber(key) or 0) then return true end
    end
    return false
end

function Input.pressed(action)
    return Input.is_down(action) and not Input._was_down(action)
end

function Input.released(action)
    return not Input.is_down(action) and Input._was_down(action)
end

function Input._was_down(action)
    for _, key in ipairs(Input._bindings[action] or {}) do
        if Input._prev[key] then return true end
    end
    return false
end

-- ────────────────────────────────────────────────────
-- 场景管理器
-- ────────────────────────────────────────────────────
local SceneManager = {}
SceneManager._current = nil
SceneManager._next = nil
SceneManager._stack = {}

function SceneManager.switch(scene)
    SceneManager._next = scene
end

function SceneManager.push(scene)
    if SceneManager._current then
        SceneManager._stack[#SceneManager._stack + 1] = SceneManager._current
        if SceneManager._current.on_pause then
            SceneManager._current:on_pause()
        end
    end
    SceneManager._current = scene
    if scene.on_enter then scene:on_enter() end
end

function SceneManager.pop()
    if SceneManager._current and SceneManager._current.on_exit then
        SceneManager._current:on_exit()
    end
    SceneManager._current = table.remove(SceneManager._stack)
    if SceneManager._current and SceneManager._current.on_resume then
        SceneManager._current:on_resume()
    end
end

function SceneManager._flush()
    if SceneManager._next then
        if SceneManager._current and SceneManager._current.on_exit then
            SceneManager._current:on_exit()
        end
        SceneManager._current = SceneManager._next
        SceneManager._next = nil
        if SceneManager._current.on_enter then
            SceneManager._current:on_enter()
        end
    end
end

function SceneManager.update(dt)
    SceneManager._flush()
    if SceneManager._current and SceneManager._current.update then
        SceneManager._current:update(dt)
    end
end

function SceneManager.draw()
    if SceneManager._current and SceneManager._current.draw then
        SceneManager._current:draw()
    end
end

function SceneManager.keypressed(key)
    if SceneManager._current and SceneManager._current.keypressed then
        SceneManager._current:keypressed(key)
    end
end

-- ────────────────────────────────────────────────────
-- 示例游戏场景
-- ────────────────────────────────────────────────────
local GameScene = {}
GameScene.__index = GameScene

function GameScene.new()
    local self = setmetatable({}, GameScene)
    self.camera = Camera.new(0, 0)
    self.entities = {}
    self.world = love.physics.newWorld(0, 500, true)

    -- 碰撞回调
    self.world:setCallbacks(
        function(a, b, coll) self:_on_begin_contact(a, b, coll) end,
        function(a, b, coll) self:_on_end_contact(a, b, coll) end
    )

    -- 示例：创建地面
    self:_create_ground()
    return self
end

function GameScene:_create_ground()
    local body = love.physics.newBody(self.world, 400, 580, "static")
    local shape = love.physics.newRectangleShape(800, 40)
    local fix = love.physics.newFixture(body, shape)
    fix:setFriction(0.8)
    self.entities[#self.entities + 1] = {
        body=body, shape=shape, fixture=fix,
        draw = function(e)
            love.graphics.setColor(0.4, 0.3, 0.2)
            local x, y = e.body:getPosition()
            love.graphics.rectangle("fill", x-400, y-20, 800, 40)
        end
    }
end

function GameScene:_on_begin_contact(a, b, coll) end
function GameScene:_on_end_contact(a, b, coll) end

function GameScene:on_enter()
    -- 绑定输入
    Input.bind("jump",  "space", "up", "w")
    Input.bind("left",  "left", "a")
    Input.bind("right", "right", "d")
    Input.bind("debug", "f1")
    self._debug = false
end

function GameScene:update(dt)
    self.world:update(dt)
    self.camera:update(dt)
    Input.update()

    for _, e in ipairs(self.entities) do
        if e.update then e:update(dt) end
    end

    if Input.pressed("debug") then
        self._debug = not self._debug
    end
end

function GameScene:draw()
    love.graphics.clear(0.1, 0.15, 0.2)

    self.camera:attach()

    -- 绘制实体
    for _, e in ipairs(self.entities) do
        if e.draw then e:draw() end
    end

    -- 调试：物理形状
    if self._debug then
        love.graphics.setColor(0, 1, 0, 0.4)
        for _, e in ipairs(self.entities) do
            if e.shape then
                local t = e.shape:getType()
                local x, y = e.body:getPosition()
                if t == "rectangle" then
                    local w, h = e.shape:getDimensions()
                    love.graphics.rectangle("line", x-w/2, y-h/2, w, h)
                elseif t == "circle" then
                    love.graphics.circle("line", x, y, e.shape:getRadius())
                end
            end
        end
    end

    self.camera:detach()

    -- HUD（不跟随摄像机）
    love.graphics.setColor(1, 1, 1)
    love.graphics.setFont(Assets.font("default", 12))
    love.graphics.print(string.format("FPS: %d", love.timer.getFPS()), 10, 10)
    if self._debug then
        love.graphics.print("DEBUG MODE (F1)", 10, 30)
    end
end

function GameScene:keypressed(key)
    if key == "escape" then love.event.quit() end
end

-- ────────────────────────────────────────────────────
-- LÖVE 主入口
-- ────────────────────────────────────────────────────
function love.load()
    -- 字体
    love.graphics.setDefaultFilter("nearest", "nearest")

    -- 启动场景
    SceneManager.push(GameScene.new())
end

function love.update(dt)
    -- 限制 dt 防止物理爆炸（暂停后恢复等情况）
    dt = math.min(dt, 1/30)
    SceneManager.update(dt)
end

function love.draw()
    SceneManager.draw()
end

function love.keypressed(key, scancode, isrepeat)
    SceneManager.keypressed(key)
end

function love.resize(w, h)
    -- 响应窗口大小变化
end

-- 导出模块（作为库使用时）
return {
    Assets   = Assets,
    Camera   = Camera,
    Input    = Input,
    SceneManager = SceneManager,
}
