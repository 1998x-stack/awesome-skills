# Animation & Tweens

## Table of Contents
1. [AnimationPlayer](#animationplayer)
2. [AnimationTree](#animationtree)
3. [Tween API (Godot 4)](#tween-api-godot-4)
4. [Sprite Animation](#sprite-animation)
5. [State Machine for Animation](#state-machine-for-animation)
6. [Procedural Animation](#procedural-animation)

---

## AnimationPlayer

### Creating Animations
AnimationPlayer is Godot's keyframe animation system. It can animate any property on any node in the scene.

```gdscript
# Play/stop animations
$AnimationPlayer.play("walk")
$AnimationPlayer.play("attack")
$AnimationPlayer.stop()
$AnimationPlayer.pause()

# Play backwards
$AnimationPlayer.play_backwards("walk")

# Play with custom blend time
$AnimationPlayer.play("walk", 0.2)  # 0.2s crossfade

# Speed control
$AnimationPlayer.speed_scale = 2.0  # Double speed

# Queue animations
$AnimationPlayer.queue("idle")  # Plays after current finishes

# Check current animation
var current: String = $AnimationPlayer.current_animation
var is_playing: bool = $AnimationPlayer.is_playing()
```

### Signals
```gdscript
$AnimationPlayer.animation_finished.connect(_on_animation_finished)
$AnimationPlayer.animation_started.connect(_on_animation_started)

func _on_animation_finished(anim_name: StringName) -> void:
    if anim_name == "attack":
        $AnimationPlayer.play("idle")
```

### Animation Method Calls
In the animation editor, you can add "Call Method" tracks that invoke functions at specific keyframes. This is useful for playing sounds, spawning particles, or applying damage at exact animation frames.

### RESET Animation
Create a special animation named "RESET" that captures the default state of all animated properties. This allows the editor to restore nodes to their original state when editing other animations.

---

## AnimationTree

AnimationTree blends between animations using a state machine or blend tree. It's essential for complex character animation.

### Setup
```gdscript
@onready var anim_tree: AnimationTree = $AnimationTree
@onready var state_machine: AnimationNodeStateMachinePlayback = anim_tree["parameters/playback"]

func _ready() -> void:
    anim_tree.active = true
```

### State Machine Transitions
```gdscript
# Travel to a state (follows transitions)
state_machine.travel("walk")

# Force immediate state change (no transition)
state_machine.start("idle")

# Get current state
var current: StringName = state_machine.get_current_node()

# Check if traveling
var is_traveling: bool = state_machine.is_playing()
```

### Blend Parameters
```gdscript
# BlendSpace2D (for 8-directional movement)
anim_tree["parameters/BlendSpace2D/blend_position"] = velocity.normalized()

# BlendTree blend amount
anim_tree["parameters/Blend2/blend_amount"] = aim_amount

# OneShot (for attack overlays)
anim_tree["parameters/OneShot/request"] = AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE
```

### BlendSpace2D Pattern (Movement)
```gdscript
func _physics_process(delta: float) -> void:
    var input := Input.get_vector("move_left", "move_right", "move_up", "move_down")

    if input != Vector2.ZERO:
        # Set blend position for directional animation
        anim_tree["parameters/Walk/blend_position"] = input
        state_machine.travel("Walk")
    else:
        state_machine.travel("Idle")
```

---

## Tween API (Godot 4)

Godot 4 completely redesigned the Tween system. Tweens are now created from any node and chained fluently.

### Basic Tween
```gdscript
# Animate a property
var tween := create_tween()
tween.tween_property($Sprite2D, "position", Vector2(200, 100), 1.0)

# Multiple properties in sequence
tween = create_tween()
tween.tween_property($Sprite2D, "position:x", 200.0, 0.5)
tween.tween_property($Sprite2D, "position:y", 100.0, 0.5)  # Starts after x finishes

# Parallel tweens (run simultaneously)
tween = create_tween()
tween.set_parallel(true)
tween.tween_property($Sprite2D, "position", Vector2(200, 100), 1.0)
tween.tween_property($Sprite2D, "modulate:a", 0.0, 1.0)
```

### Tween Methods
```gdscript
var tween := create_tween()

# Animate property
tween.tween_property(node, "property", target_value, duration)

# From a specific value
tween.tween_property(node, "position", Vector2(200, 0), 1.0).from(Vector2.ZERO)

# Relative (add to current value)
tween.tween_property(node, "position", Vector2(100, 0), 0.5).as_relative()

# Call a method
tween.tween_callback(func(): print("done"))
tween.tween_callback(queue_free)  # Free node after animation

# Wait
tween.tween_interval(0.5)  # Pause for 0.5 seconds

# Animate via method (custom setter)
tween.tween_method(set_health_display, 100.0, 0.0, 2.0)
```

### Easing & Transitions
```gdscript
var tween := create_tween()

# Set easing for all subsequent steps
tween.set_ease(Tween.EASE_OUT)
tween.set_trans(Tween.TRANS_ELASTIC)

# Per-step easing
tween.tween_property($Sprite2D, "scale", Vector2(2, 2), 0.3) \
    .set_ease(Tween.EASE_OUT) \
    .set_trans(Tween.TRANS_BACK)

# Common transitions:
# TRANS_LINEAR  — constant speed
# TRANS_SINE    — smooth sine wave
# TRANS_CUBIC   — acceleration curve
# TRANS_BACK    — overshoots then returns
# TRANS_ELASTIC — springy bounce
# TRANS_BOUNCE  — bouncing ball
# TRANS_EXPO    — exponential
```

### Looping Tweens
```gdscript
# Loop forever
var tween := create_tween().set_loops()  # Infinite loops
tween.tween_property($Sprite2D, "rotation", TAU, 2.0)

# Loop N times
tween = create_tween().set_loops(3)

# Ping-pong (back and forth)
# No built-in ping-pong, but achievable:
tween = create_tween().set_loops()
tween.tween_property($Sprite2D, "position:y", -20.0, 0.5).as_relative()
tween.tween_property($Sprite2D, "position:y", 20.0, 0.5).as_relative()
```

### Tween Signals & Control
```gdscript
var tween := create_tween()
tween.tween_property($Sprite2D, "position", Vector2(200, 0), 1.0)

# Wait for completion
await tween.finished

# Control
tween.pause()
tween.play()
tween.stop()     # Stops and resets
tween.kill()     # Removes the tween
tween.is_running()
tween.is_valid()  # False after kill() or node freed
```

### Common Tween Recipes
```gdscript
# Hit flash (white flash then return)
func flash_white() -> void:
    var tween := create_tween()
    tween.tween_property($Sprite2D, "modulate", Color.WHITE, 0.05)
    tween.tween_property($Sprite2D, "modulate", Color(1, 1, 1, 1), 0.1)

# Damage shake
func shake(intensity: float = 5.0, duration: float = 0.2) -> void:
    var original_pos: Vector2 = position
    var tween := create_tween()
    for i in 5:
        var offset := Vector2(
            randf_range(-intensity, intensity),
            randf_range(-intensity, intensity)
        )
        tween.tween_property(self, "position", original_pos + offset, duration / 5.0)
    tween.tween_property(self, "position", original_pos, duration / 5.0)

# Scale pop (juice)
func pop_scale() -> void:
    var tween := create_tween()
    tween.tween_property(self, "scale", Vector2(1.2, 1.2), 0.1) \
        .set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
    tween.tween_property(self, "scale", Vector2.ONE, 0.15) \
        .set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_BACK)

# Fade in/out
func fade_in(duration: float = 0.3) -> void:
    modulate.a = 0.0
    var tween := create_tween()
    tween.tween_property(self, "modulate:a", 1.0, duration)

func fade_out_and_free(duration: float = 0.3) -> void:
    var tween := create_tween()
    tween.tween_property(self, "modulate:a", 0.0, duration)
    tween.tween_callback(queue_free)
```

---

## Sprite Animation

### AnimatedSprite2D
For simple frame-based animations (pixel art, etc.):

```gdscript
@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D

func _physics_process(delta: float) -> void:
    if velocity.length() > 0:
        sprite.play("walk")
        sprite.flip_h = velocity.x < 0
    else:
        sprite.play("idle")

# Signals
sprite.animation_finished.connect(_on_animation_finished)
sprite.frame_changed.connect(_on_frame_changed)
```

### Sprite2D + AnimationPlayer
For more control, animate Sprite2D properties with AnimationPlayer:
- `frame` property for frame-by-frame
- `region_rect` for spritesheet regions
- `flip_h` / `flip_v` for direction

---

## State Machine for Animation

### Simple Animation State Machine
```gdscript
# anim_state_machine.gd
extends Node

enum State { IDLE, WALK, RUN, JUMP, FALL, ATTACK }

var current_state: State = State.IDLE
@onready var anim: AnimationPlayer = $"../AnimationPlayer"
@onready var sprite: Sprite2D = $"../Sprite2D"

func transition(new_state: State) -> void:
    if new_state == current_state:
        return
    _exit_state(current_state)
    current_state = new_state
    _enter_state(new_state)

func _enter_state(state: State) -> void:
    match state:
        State.IDLE:
            anim.play("idle")
        State.WALK:
            anim.play("walk")
        State.JUMP:
            anim.play("jump")
        State.FALL:
            anim.play("fall")
        State.ATTACK:
            anim.play("attack")
            await anim.animation_finished
            transition(State.IDLE)

func _exit_state(state: State) -> void:
    pass  # Cleanup if needed
```

---

## Procedural Animation

### Look-At with Smoothing
```gdscript
func _process(delta: float) -> void:
    var target_angle: float = global_position.angle_to_point(target.global_position)
    rotation = lerp_angle(rotation, target_angle, delta * 10.0)
```

### Squash & Stretch
```gdscript
func apply_squash(intensity: float = 0.3) -> void:
    scale = Vector2(1.0 + intensity, 1.0 - intensity)
    var tween := create_tween()
    tween.tween_property(self, "scale", Vector2.ONE, 0.15) \
        .set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_ELASTIC)

func apply_stretch(intensity: float = 0.3) -> void:
    scale = Vector2(1.0 - intensity, 1.0 + intensity)
    var tween := create_tween()
    tween.tween_property(self, "scale", Vector2.ONE, 0.15) \
        .set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_ELASTIC)
```

### Trail Effect
```gdscript
func spawn_trail() -> void:
    var ghost := Sprite2D.new()
    ghost.texture = sprite.texture
    ghost.global_position = global_position
    ghost.global_rotation = global_rotation
    ghost.scale = scale
    ghost.modulate.a = 0.5
    get_tree().current_scene.add_child(ghost)

    var tween := ghost.create_tween()
    tween.tween_property(ghost, "modulate:a", 0.0, 0.3)
    tween.tween_callback(ghost.queue_free)
```
