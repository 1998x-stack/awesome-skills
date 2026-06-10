---
name: godot-engine
description: Godot 4.x game engine development skill. Activate when users work on Godot projects, write GDScript, create scenes/nodes, design game systems, debug Godot issues, set up physics/UI/animations/shaders, or do anything involving .gd/.tscn/.tres files. Also trigger for questions about Godot 3-to-4 migration, GDScript best practices, Godot node architecture, signal patterns, CharacterBody movement, or Godot project structure. Even casual mentions like "my Godot project", "GDScript error", "scene tree problem", or "how do I do X in Godot" should activate this skill.
---

# Godot 4.x Game Engine Development

## What This Skill Does

Turns Claude into a Godot 4.x expert that writes idiomatic GDScript, designs clean scene architectures, and avoids the engine's many subtle pitfalls. The skill covers the full stack: GDScript language, node/scene design, physics, UI, animation, shaders, multiplayer, and project organization.

> **Core philosophy:** Godot's power is composition. Scenes are your classes, nodes are your components, signals are your interfaces. Work *with* the scene tree, not against it.

---

## Quick Decision: Which Reference to Read

Load the relevant reference file based on what the user needs:

| Task | Reference File |
|------|---------------|
| Writing GDScript, type hints, signals, coroutines, exports | `references/gdscript-patterns.md` |
| Scene architecture, node lifecycle, composition, autoloads | `references/node-architecture.md` |
| CharacterBody, RigidBody, Area, collision layers, raycasts | `references/physics-and-movement.md` |
| Control nodes, themes, responsive UI, HUD | `references/ui-and-themes.md` |
| Visual effects, materials, screen-space effects | `references/shaders.md` |
| AnimationPlayer, AnimationTree, Tween, state machines | `references/animation-and-tweens.md` |
| Godot 3 to 4 migration, common mistakes, debugging | `references/common-pitfalls.md` |
| Networking, RPCs, multiplayer synchronization | `references/multiplayer.md` |
| Project layout, naming conventions, export/build | `references/project-structure.md` |

For complex tasks, load multiple references. When unsure, start with `gdscript-patterns.md` and `common-pitfalls.md`.

---

## The Golden Rules

These rules prevent the most common Godot mistakes. Internalize them before writing any code:

### 1. Call Down, Signal Up
Parents call methods on children directly. Children emit signals that parents connect to. Never use `get_parent()` to call parent methods — it creates invisible dependencies.

```gdscript
# GOOD: Parent connects to child signal
func _ready() -> void:
    $HealthComponent.health_depleted.connect(_on_health_depleted)

# BAD: Child reaches up to parent
func take_damage(amount: int) -> void:
    get_parent().die()  # Fragile! What if parent changes?
```

### 2. Always Use Static Typing
Statically typed GDScript runs 40%+ faster and catches bugs at parse time. Type everything: variables, parameters, return values.

```gdscript
# GOOD
var speed: float = 200.0
func get_damage() -> int:
    return base_damage * multiplier

# BAD
var speed = 200.0
func get_damage():
    return base_damage * multiplier
```

### 3. Cache Node References with @onready
Never call `get_node()` or use `$` in `_process()`. Cache references once at startup.

```gdscript
# GOOD
@onready var sprite: Sprite2D = $Sprite2D
@onready var collision: CollisionShape2D = $CollisionShape2D

func _process(delta: float) -> void:
    sprite.rotation += delta  # Cached, zero cost

# BAD
func _process(delta: float) -> void:
    $Sprite2D.rotation += delta  # Tree traversal 60x/sec!
```

### 4. Compose with Scenes, Not Inheritance
Deep inheritance hierarchies fight Godot's design. Instead, build entities by combining small, reusable component scenes.

```
Player.tscn
├── CharacterBody2D (root)
├── Sprite2D
├── CollisionShape2D
├── HealthComponent.tscn    (reusable)
├── HitboxComponent.tscn    (reusable)
└── StateMachine.tscn       (reusable)
```

### 5. Physics in _physics_process(), Visuals in _process()
`_process()` runs at monitor refresh rate (variable). `_physics_process()` runs at fixed 60Hz. Mixing them causes jitter and inconsistent behavior.

```gdscript
func _physics_process(delta: float) -> void:
    velocity = direction * speed
    move_and_slide()  # Physics here

func _process(delta: float) -> void:
    sprite.rotation = velocity.angle()  # Visuals here
```

---

## GDScript Quick Reference

### Signals (Godot 4 Syntax)
```gdscript
# Declaration
signal health_changed(new_health: int)
signal died

# Emission
health_changed.emit(current_health)
died.emit()

# Connection (code)
health_bar.health_changed.connect(_on_health_changed)

# Connection (one-shot)
timer.timeout.connect(_on_timeout, CONNECT_ONE_SHOT)

# Disconnection
health_bar.health_changed.disconnect(_on_health_changed)

# Awaiting signals
await get_tree().create_timer(1.0).timeout
var result = await $HTTPRequest.request_completed
```

### Exports
```gdscript
@export var speed: float = 100.0
@export var health: int = 100
@export var weapon_scene: PackedScene
@export_range(0, 100, 1) var volume: int = 50
@export_enum("Sword", "Bow", "Staff") var weapon_type: int = 0
@export_file("*.tscn") var level_path: String
@export_group("Movement")
@export var max_speed: float = 400.0
@export var acceleration: float = 200.0
@export_subgroup("Jumping")
@export var jump_force: float = 300.0
@export_category("Combat")  # Creates a new category header
```

### Resources (Data Objects)
```gdscript
# weapon_data.gd
class_name WeaponData
extends Resource

@export var name: String
@export var damage: int
@export var attack_speed: float
@export var icon: Texture2D

# Usage
@export var weapon: WeaponData  # Editable in inspector!
```

### Common Patterns
```gdscript
# Scene instantiation
var bullet: Bullet = bullet_scene.instantiate()
get_tree().current_scene.add_child(bullet)
bullet.global_position = global_position  # Set AFTER add_child

# Deferred calls (safe during callbacks)
call_deferred("add_child", node)
set_deferred("monitoring", true)

# Groups
add_to_group("enemies")
get_tree().get_nodes_in_group("enemies")
get_tree().call_group("enemies", "take_damage", 10)

# Timer (one-liner)
await get_tree().create_timer(0.5).timeout
```

---

## Common File Patterns

### .tscn Scene File Structure
```ini
[gd_scene load_steps=3 format=3 uid="uid://abc123"]

[ext_resource type="Script" path="res://scripts/player.gd" id="1"]
[ext_resource type="Texture2D" path="res://sprites/player.png" id="2"]

[sub_resource type="RectangleShape2D" id="SubResource_1"]
size = Vector2(16, 32)

[node name="Player" type="CharacterBody2D"]
script = ExtResource("1")
speed = 200.0

[node name="Sprite2D" type="Sprite2D" parent="."]
texture = ExtResource("2")

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("SubResource_1")

[connection signal="body_entered" from="." to="." method="_on_body_entered"]
```

### project.godot Essentials
```ini
[application]
config/name="MyGame"
run/main_scene="res://scenes/main.tscn"

[autoload]
GameManager="*res://scripts/autoloads/game_manager.gd"
EventBus="*res://scripts/autoloads/event_bus.gd"

[display]
window/size/viewport_width=1920
window/size/viewport_height=1080
window/stretch/mode="canvas_items"
window/stretch/aspect="keep"

[input]
move_left={
"deadzone": 0.5,
"events": [Object(InputEventKey,"keycode":65)]
}

[layer_names]
2d_physics/layer_1="Player"
2d_physics/layer_2="Enemies"
2d_physics/layer_3="Environment"
2d_physics/layer_4="Projectiles"
```

---

## Utility Scripts

The `scripts/` directory contains helper scripts:

| Script | Purpose |
|--------|---------|
| `scripts/scaffold_project.py` | Generate a standard Godot project directory structure |
| `scripts/scene_template.py` | Generate .tscn files from templates (player, enemy, UI, level) |
| `scripts/gdscript_lint.py` | Lint and auto-fix common GDScript issues |

Run them with `python scripts/<name>.py --help` for usage.

---

## File Structure

```
godot-engine/
├── SKILL.md                          <- You are here
├── references/
│   ├── gdscript-patterns.md          <- GDScript language deep-dive
│   ├── node-architecture.md          <- Scene tree, lifecycle, composition
│   ├── physics-and-movement.md       <- CharacterBody, RigidBody, collision
│   ├── ui-and-themes.md              <- Control nodes, themes, responsive UI
│   ├── shaders.md                    <- Godot shader language
│   ├── animation-and-tweens.md       <- AnimationPlayer, Tween, state machines
│   ├── common-pitfalls.md            <- Godot 3->4 migration, gotchas
│   ├── multiplayer.md                <- Networking, RPCs, sync
│   └── project-structure.md          <- File layout, naming, export
└── scripts/
    ├── scaffold_project.py           <- Project scaffolding
    ├── scene_template.py             <- .tscn generation
    └── gdscript_lint.py              <- GDScript linter
```
