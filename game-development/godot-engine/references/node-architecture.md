# Node & Scene Architecture

## Table of Contents
1. [Node Lifecycle](#node-lifecycle)
2. [Scene Composition](#scene-composition)
3. [Autoloads & Singletons](#autoloads--singletons)
4. [Scene Instantiation](#scene-instantiation)
5. [Node Groups](#node-groups)
6. [Scene Tree Navigation](#scene-tree-navigation)
7. [Component Pattern](#component-pattern)

---

## Node Lifecycle

### Callback Order
```
_init()                  # Constructor (before added to tree)
_enter_tree()            # Added to scene tree (may run multiple times)
_ready()                 # All children are ready (runs once unless re-entering tree)
_process(delta)          # Every frame (variable rate)
_physics_process(delta)  # Every physics tick (fixed 60Hz)
_input(event)            # Unhandled input (before GUI)
_unhandled_input(event)  # Input not consumed by GUI
_exit_tree()             # Removed from scene tree
_notification(what)      # Low-level notifications
```

### Key Rules
- `_ready()` is called bottom-up: children are ready before parents
- `_ready()` runs once by default. Use `request_ready()` to make it run again on next tree entry
- `_enter_tree()` runs every time the node enters the tree (including after `remove_child` + `add_child`)
- `_process()` runs at monitor refresh rate (60-240+ FPS)
- `_physics_process()` runs at fixed rate (default 60Hz, configurable in project settings)

### Common Lifecycle Patterns
```gdscript
func _ready() -> void:
    # Initialize state, connect signals, set up references
    $HealthBar.max_value = max_health
    $HealthBar.value = current_health
    $HitboxArea.body_entered.connect(_on_hitbox_body_entered)

func _process(delta: float) -> void:
    # Visual updates, animations, non-physics interpolation
    sprite.global_position = sprite.global_position.lerp(target_pos, delta * 10)

func _physics_process(delta: float) -> void:
    # Movement, collision, physics calculations
    velocity.y += gravity * delta
    move_and_slide()

func _exit_tree() -> void:
    # Cleanup: disconnect external signals, free resources
    EventBus.game_paused.disconnect(_on_game_paused)
```

---

## Scene Composition

### The Principle
Scenes are Godot's unit of composition — think of them as reusable, self-contained components. Build complex entities by nesting scenes, not by creating deep class hierarchies.

### Entity Composition Example
```
# Player.tscn
Player (CharacterBody2D)
├── Sprite2D
├── CollisionShape2D
├── AnimationPlayer
├── Camera2D
├── HealthComponent.tscn     # Reusable across player/enemies
├── HurtboxComponent.tscn    # Takes damage
├── HitboxComponent.tscn     # Deals damage
├── StateMachine.tscn         # Manages player states
│   ├── IdleState
│   ├── RunState
│   ├── JumpState
│   └── AttackState
└── InteractionArea (Area2D)  # Detects interactable objects
```

### Component Communication
Components communicate via signals — they don't know about each other directly.

```gdscript
# health_component.gd
class_name HealthComponent
extends Node

signal health_changed(current: int, maximum: int)
signal died

@export var max_health: int = 100
var current_health: int

func _ready() -> void:
    current_health = max_health

func take_damage(amount: int) -> void:
    current_health = max(0, current_health - amount)
    health_changed.emit(current_health, max_health)
    if current_health == 0:
        died.emit()

func heal(amount: int) -> void:
    current_health = min(max_health, current_health + amount)
    health_changed.emit(current_health, max_health)
```

```gdscript
# In Player._ready() — wire components together
func _ready() -> void:
    $HealthComponent.died.connect(_on_died)
    $HealthComponent.health_changed.connect($HealthBar.update_display)
    $HurtboxComponent.damage_received.connect($HealthComponent.take_damage)
```

---

## Autoloads & Singletons

Autoloads are nodes that persist across scene changes. Set them in Project Settings > AutoLoad.

### When to Use Autoloads
- **Global game state** (score, player data, settings)
- **Event bus** (global signal hub)
- **Scene transitions** (fade effects between scenes)
- **Audio manager** (music that plays across scenes)
- **Save/load system**

### When NOT to Use Autoloads
- Game logic that belongs to a specific scene
- Anything that should reset between levels
- Data that only one system needs

### Autoload Examples
```gdscript
# autoloads/game_manager.gd
extends Node

var score: int = 0
var current_level: int = 1
var player_data: PlayerData

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS  # Run even when paused

func reset() -> void:
    score = 0
    current_level = 1
```

```gdscript
# autoloads/scene_manager.gd
extends Node

signal scene_changed

func change_scene(path: String) -> void:
    # Fade out
    var tween := create_tween()
    tween.tween_property($ColorRect, "color:a", 1.0, 0.3)
    await tween.finished

    get_tree().change_scene_to_file(path)
    scene_changed.emit()

    # Fade in
    tween = create_tween()
    tween.tween_property($ColorRect, "color:a", 0.0, 0.3)
```

---

## Scene Instantiation

### Basic Instantiation
```gdscript
@export var bullet_scene: PackedScene

func shoot() -> void:
    var bullet: Bullet = bullet_scene.instantiate()
    # Add to scene tree FIRST
    get_tree().current_scene.add_child(bullet)
    # Set position AFTER add_child (needs parent transform)
    bullet.global_position = $Muzzle.global_position
    bullet.rotation = rotation
    bullet.direction = Vector2.RIGHT.rotated(rotation)
```

### Preloading vs Loading
```gdscript
# preload: resolved at parse time (instant, but increases load time)
const BULLET := preload("res://scenes/bullet.tscn")

# load: resolved at runtime (slight delay, but lazy)
var bullet_scene: PackedScene = load("res://scenes/bullet.tscn")

# ResourceLoader: async loading (best for large assets)
func _ready() -> void:
    ResourceLoader.load_threaded_request("res://levels/level_2.tscn")

func _process(_delta: float) -> void:
    var status := ResourceLoader.load_threaded_get_status("res://levels/level_2.tscn")
    if status == ResourceLoader.THREAD_LOAD_LOADED:
        var scene: PackedScene = ResourceLoader.load_threaded_get("res://levels/level_2.tscn")
```

### Deferred Instantiation
```gdscript
# Safe during physics callbacks or signal handlers
func _on_enemy_died() -> void:
    var explosion := explosion_scene.instantiate()
    add_child.call_deferred(explosion)  # Wait until end of frame
    explosion.global_position = global_position  # OK: set before deferred add
```

---

## Node Groups

Groups are tags for nodes. Use them for batch operations.

```gdscript
# Add to group
add_to_group("enemies")
add_to_group("damageable")

# Check membership
if is_in_group("enemies"):
    pass

# Get all nodes in group
var enemies: Array[Node] = get_tree().get_nodes_in_group("enemies")

# Call method on all group members
get_tree().call_group("enemies", "alert", player_position)

# Deferred group call (safe during physics)
get_tree().call_group_flags(
    SceneTree.GROUP_CALL_DEFERRED,
    "enemies",
    "take_damage",
    50
)

# Notify group (via _notification)
get_tree().notify_group("enemies", NOTIFICATION_CUSTOM)
```

---

## Scene Tree Navigation

### Getting Nodes
```gdscript
# Shorthand for get_node()
$Sprite2D                    # Direct child
$"Path/To/Deep/Node"        # Path with special chars
%UniqueNode                  # Scene-unique node (best practice)

# get_node with typed result
var sprite: Sprite2D = get_node("Sprite2D") as Sprite2D

# Scene-unique nodes (set in editor: right-click > "Access as Unique Name")
# Allows referencing without knowing full path
@onready var health_bar: ProgressBar = %HealthBar
```

### Tree Traversal
```gdscript
# Parent
var parent: Node = get_parent()

# Children
for child in get_children():
    if child is Enemy:
        child.alert()

# Owner (root of the scene this node belongs to)
var scene_root: Node = owner

# Current scene root
var scene: Node = get_tree().current_scene

# Find first child of type
func find_child_of_type(parent_node: Node, type: GDScript) -> Node:
    for child in parent_node.get_children():
        if child is type:
            return child
    return null
```

### Scene-Unique Nodes (% prefix)
The `%` prefix accesses nodes marked as "unique" in their scene. This is the recommended way to reference nodes because it survives reparenting within the scene.

```gdscript
# Set in editor: Right-click node > "Access as Unique Name"
# Then reference from anywhere in the same scene:
@onready var health_label: Label = %HealthLabel
@onready var score_display: Label = %ScoreDisplay
```

---

## Component Pattern

### Base Component
```gdscript
# components/component.gd
class_name GameComponent
extends Node

# Override in subclasses
func initialize(entity: Node) -> void:
    pass
```

### Hitbox/Hurtbox System
```gdscript
# components/hitbox_component.gd
class_name HitboxComponent
extends Area2D

@export var damage: int = 10

# Hurtbox detects this hitbox entering
```

```gdscript
# components/hurtbox_component.gd
class_name HurtboxComponent
extends Area2D

signal damage_received(amount: int)

func _ready() -> void:
    area_entered.connect(_on_area_entered)

func _on_area_entered(hitbox: Area2D) -> void:
    if hitbox is HitboxComponent:
        damage_received.emit(hitbox.damage)
```

### Wiring Components in the Entity Root
```gdscript
# player.gd
extends CharacterBody2D

@onready var health: HealthComponent = $HealthComponent
@onready var hurtbox: HurtboxComponent = $HurtboxComponent

func _ready() -> void:
    hurtbox.damage_received.connect(health.take_damage)
    health.died.connect(_on_died)

func _on_died() -> void:
    queue_free()
```
