# GDScript Patterns & Best Practices

## Table of Contents
1. [Type System](#type-system)
2. [Signals Deep Dive](#signals-deep-dive)
3. [Coroutines & Await](#coroutines--await)
4. [Export Annotations](#export-annotations)
5. [Resources as Data Objects](#resources-as-data-objects)
6. [Enums & Constants](#enums--constants)
7. [Lambdas & Callables](#lambdas--callables)
8. [Static Functions & class_name](#static-functions--class_name)
9. [Tool Scripts](#tool-scripts)
10. [Design Patterns in GDScript](#design-patterns-in-gdscript)

---

## GDScript is NOT Python

GDScript syntax resembles Python but has critical differences. LLMs frequently generate Python code that fails silently or crashes in Godot.

### Indentation: Tabs Only
```gdscript
# Godot 4 GDScript REQUIRES tab indentation.
# Space-indented code silently fails to parse — no error, just doesn't load.
# This is the #1 cause of unexplained timeouts.
func _ready():
	var x = 1   # TAB — correct
	pass         # TAB — correct
```

### Methods That Don't Exist
| Python | GDScript Equivalent |
|--------|-------------------|
| `len(array)` | `array.size()` |
| `enumerate(array)` | `for i in range(array.size()):` then `array[i]` |
| `"{}".format(x)` | `"%s" % x` or `"%d" % x` |
| `str.join(list)` | `", ".join(PackedStringArray(list))` |
| `array.sort(key=...)` | `array.sort_custom(func(a,b): return ...)` |
| `array.append(x)` | `array.append(x)` (same!) |
| `dict.items()` | `for key in dict:` then `dict[key]` |
| `dict.keys()` | `dict.keys()` (same!) |
| `isinstance(x, T)` | `x is T` |
| `list.pop(0)` | `array.pop_front()` |
| `array.empty()` | `array.is_empty()` (Godot 4) |

### String Formatting
```gdscript
# GDScript uses % operator, NOT .format() or f-strings:
var text = "Score: %d" % score
var text2 = "%s has %d HP" % [name, health]
var text3 = "Position: %s" % str(position)

# Padding/formatting:
var padded = "%02d/%02d" % [current, total]    # "03/10"
var float_fmt = "%.2f" % value                  # "3.14"
```

### _to_string() Best Practice
Use `PackedStringArray` + `join()` for predictable output without trailing delimiters:
```gdscript
func _to_string() -> String:
	var parts := PackedStringArray()
	for item in items:
		parts.append(str(item))
	return ", ".join(parts)
```

### Variant Type Inference
The `:=` operator infers type from the right side. Functions returning `Variant` (like `pop_front()`, `Dictionary.get()`) cause parse errors with `:=`:
```gdscript
# WRONG — parse error:
var card := cards.pop_front()

# CORRECT:
var card = cards.pop_front()
```

---

## Type System

### Static Typing Rules
Always use static typing. It provides 40%+ performance gains and catches bugs at parse time.

```gdscript
# Typed variables
var health: int = 100
var speed: float = 200.0
var player_name: String = "Hero"
var position: Vector2 = Vector2.ZERO
var items: Array[String] = []
var stats: Dictionary[String, int] = {}  # Godot 4.4+

# Typed function signatures
func calculate_damage(base: int, multiplier: float) -> int:
    return int(base * multiplier)

# Typed arrays
var enemies: Array[Enemy] = []
var scores: Array[int] = [10, 20, 30]

# Typed dictionaries (Godot 4.4+)
var inventory: Dictionary[String, int] = {"sword": 1, "potion": 5}
```

### Type Casting
```gdscript
# Safe cast with `as` (returns null on failure for Objects)
var enemy := node as Enemy
if enemy:
    enemy.take_damage(10)

# DANGER: `as` on built-in types THROWS an error on failure
# var x := value as int  # Crashes if value isn't int-compatible

# Use `is` for type checking
if node is CharacterBody2D:
    node.move_and_slide()
```

### Null Safety Pattern
```gdscript
# Check before use
var target: Node2D = get_closest_enemy()
if target:
    look_at(target.global_position)

# is_instance_valid for potentially freed nodes
if is_instance_valid(target):
    target.take_damage(10)
```

---

## Signals Deep Dive

### Declaration
```gdscript
# No parameters
signal died

# With typed parameters
signal health_changed(new_health: int, max_health: int)
signal item_collected(item: ItemData)

# Note: Parameter type annotations are documentation only.
# Godot does NOT validate types at emission time.
```

### Emission
```gdscript
health_changed.emit(current_health, max_health)
died.emit()
```

### Connection Patterns
```gdscript
# Direct connection
$Button.pressed.connect(_on_button_pressed)

# One-shot (auto-disconnects after first emission)
$Timer.timeout.connect(_on_timeout, CONNECT_ONE_SHOT)

# Deferred (called at end of frame, safe during physics)
signal_name.connect(handler, CONNECT_DEFERRED)

# With bind (pass extra arguments)
for i in range(3):
    buttons[i].pressed.connect(_on_slot_pressed.bind(i))

# Lambda connection (be careful — can't disconnect easily)
$Button.pressed.connect(func(): print("clicked"))
```

### Signal Safety
```gdscript
# Prevent duplicate connections
if not health_changed.is_connected(_on_health_changed):
    health_changed.connect(_on_health_changed)

# Safe disconnection
if health_changed.is_connected(_on_health_changed):
    health_changed.disconnect(_on_health_changed)

# WARNING: Signals can fire AFTER queue_free() until end of frame
# WARNING: Awaiting a signal from a freed node hangs forever
```

### Signal Bus Pattern (Event Bus)
```gdscript
# autoloads/event_bus.gd
extends Node

signal player_died
signal score_changed(new_score: int)
signal level_completed(level_id: int)

# Usage anywhere:
EventBus.player_died.emit()
EventBus.score_changed.connect(_on_score_changed)
```

---

## Coroutines & Await

### Basic Await
```gdscript
# Wait for a signal
await $AnimationPlayer.animation_finished

# Wait for a timer
await get_tree().create_timer(1.5).timeout

# Wait for next frame
await get_tree().process_frame

# Wait for physics frame
await get_tree().physics_frame
```

### Async Function Pattern
```gdscript
func fade_out(duration: float) -> void:
    var tween := create_tween()
    tween.tween_property($Sprite2D, "modulate:a", 0.0, duration)
    await tween.finished

func death_sequence() -> void:
    $AnimationPlayer.play("death")
    await $AnimationPlayer.animation_finished
    await fade_out(0.5)
    queue_free()
```

### Dangers of Await
```gdscript
# DANGER: If the node is freed while awaiting, the coroutine dies silently
# DANGER: If the signal source is freed, await hangs forever

# Safe pattern: check validity after await
await get_tree().create_timer(1.0).timeout
if not is_instance_valid(self):
    return  # Node was freed during await
```

---

## Export Annotations

```gdscript
# Basic exports
@export var speed: float = 100.0
@export var scene: PackedScene
@export var texture: Texture2D

# Ranges
@export_range(0, 100) var health: int = 100
@export_range(0.0, 1.0, 0.01) var opacity: float = 1.0
@export_range(0, 1000, 1, "or_greater") var damage: int = 10

# Enums
@export_enum("Idle", "Walking", "Running") var state: int = 0
@export_enum("Fire", "Ice", "Lightning") var element: String = "Fire"

# File/directory
@export_file("*.tscn") var level_path: String
@export_dir var save_directory: String

# Multi-line text
@export_multiline var description: String

# Colors
@export_color_no_alpha var tint: Color = Color.WHITE

# Grouping
@export_group("Movement")
@export var max_speed: float = 400.0
@export var friction: float = 0.9
@export_subgroup("Jump")
@export var jump_height: float = 200.0
@export var gravity_scale: float = 1.0

# Categories (big section headers)
@export_category("Combat Stats")
@export var attack: int = 10
@export var defense: int = 5

# Flags (bitfield)
@export_flags("Fire", "Water", "Earth", "Wind") var elements: int

# Node paths
@export var target_path: NodePath

# Tool button (Godot 4.4+)
# @export_tool_button("Run Setup") var _setup = _do_setup
```

---

## Resources as Data Objects

Resources are Godot's data containers — like scriptable objects in Unity. They are saved as `.tres` files and are shared by reference.

```gdscript
# weapon_data.gd
class_name WeaponData
extends Resource

@export var name: String = ""
@export var damage: int = 10
@export var attack_speed: float = 1.0
@export var range_meters: float = 1.5
@export var icon: Texture2D
@export var sound_effect: AudioStream

func get_dps() -> float:
    return damage * attack_speed
```

```gdscript
# Using resources
@export var weapon: WeaponData

func attack() -> void:
    var dmg: int = weapon.damage
    $AudioStreamPlayer.stream = weapon.sound_effect
    $AudioStreamPlayer.play()
```

### Resource Sharing Warning
Resources loaded from files are shared by default. If two enemies load the same WeaponData resource and one modifies it, both are affected.

```gdscript
# To get an independent copy:
var my_weapon: WeaponData = weapon.duplicate()
```

---

## Enums & Constants

```gdscript
enum State { IDLE, WALKING, RUNNING, JUMPING }
enum Team { PLAYER = 1, ENEMY = 2, NEUTRAL = 0 }

var current_state: State = State.IDLE

# Enums are ints under the hood
# WARNING: var x: State = 999 compiles even if 999 isn't valid!

# Constants
const MAX_SPEED: float = 400.0
const GRAVITY: float = 980.0
const TILE_SIZE: int = 16
```

---

## Lambdas & Callables

```gdscript
# Lambda
var double := func(x: int) -> int: return x * 2

# As callback
enemies.sort_custom(func(a: Enemy, b: Enemy) -> bool:
    return a.health < b.health
)

# Filter/map patterns
var alive: Array[Enemy] = enemies.filter(func(e: Enemy) -> bool: return e.health > 0)
var names: Array[String] = enemies.map(func(e: Enemy) -> String: return e.name)

# Callable.bind
var greet := func(name: String, greeting: String) -> void:
    print(greeting + " " + name)
var hello := greet.bind("World")
```

---

## Static Functions & class_name

```gdscript
# math_utils.gd
class_name MathUtils

static func lerp_angle_degrees(from: float, to: float, weight: float) -> float:
    var diff := fmod(to - from + 180.0, 360.0) - 180.0
    return from + diff * weight

# Usable anywhere without instantiation:
var angle := MathUtils.lerp_angle_degrees(current, target, 0.1)
```

---

## Tool Scripts

`@tool` scripts run in the editor. Use for custom previews, gizmos, and editor plugins.

```gdscript
@tool
extends Node2D

@export var radius: float = 50.0:
    set(value):
        radius = value
        queue_redraw()  # Redraw in editor when changed

func _draw() -> void:
    draw_circle(Vector2.ZERO, radius, Color.RED)
```

**Safety rule:** Always guard game logic with `Engine.is_editor_hint()`:
```gdscript
func _process(delta: float) -> void:
    if Engine.is_editor_hint():
        return  # Don't run game logic in editor
    move_and_slide()
```

---

## Design Patterns in GDScript

### State Machine
```gdscript
class_name StateMachine
extends Node

@export var initial_state: State
var current_state: State

func _ready() -> void:
    for child in get_children():
        if child is State:
            child.state_machine = self
    current_state = initial_state
    current_state.enter()

func _process(delta: float) -> void:
    current_state.update(delta)

func _physics_process(delta: float) -> void:
    current_state.physics_update(delta)

func transition_to(target_state_name: String) -> void:
    var new_state: State = get_node(target_state_name) as State
    if not new_state:
        return
    current_state.exit()
    current_state = new_state
    current_state.enter()
```

### Object Pool
```gdscript
class_name ObjectPool
extends Node

@export var scene: PackedScene
@export var pool_size: int = 20

var _pool: Array[Node] = []

func _ready() -> void:
    for i in pool_size:
        var instance := scene.instantiate()
        instance.visible = false
        instance.set_process(false)
        add_child(instance)
        _pool.append(instance)

func get_instance() -> Node:
    for obj in _pool:
        if not obj.visible:
            obj.visible = true
            obj.set_process(true)
            return obj
    # Pool exhausted — expand
    var instance := scene.instantiate()
    add_child(instance)
    _pool.append(instance)
    return instance

func release(obj: Node) -> void:
    obj.visible = false
    obj.set_process(false)
```

### Command Pattern (Input)
```gdscript
class_name InputCommand
extends RefCounted

var action: Callable

func _init(action_callable: Callable) -> void:
    action = action_callable

func execute() -> void:
    action.call()

# Usage
var jump_command := InputCommand.new(player.jump)
var attack_command := InputCommand.new(player.attack)
```
