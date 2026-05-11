# Common Pitfalls & Godot 3-to-4 Migration

## Table of Contents
1. [Godot 3 to 4 Breaking Changes](#godot-3-to-4-breaking-changes)
2. [Top 15 GDScript Mistakes](#top-15-gdscript-mistakes)
3. [Performance Pitfalls](#performance-pitfalls)
4. [Debugging Techniques](#debugging-techniques)
5. [Editor Gotchas](#editor-gotchas)

---

## Godot 3 to 4 Breaking Changes

### Signal Syntax
```gdscript
# Godot 3
connect("signal_name", target, "_method_name")
emit_signal("signal_name", arg1, arg2)
disconnect("signal_name", target, "_method_name")

# Godot 4
signal_name.connect(_method_name)
signal_name.emit(arg1, arg2)
signal_name.disconnect(_method_name)
```

### Tween API
```gdscript
# Godot 3
var tween = Tween.new()
add_child(tween)
tween.interpolate_property(sprite, "modulate:a", 1.0, 0.0, 0.5)
tween.start()

# Godot 4
var tween = create_tween()
tween.tween_property(sprite, "modulate:a", 0.0, 0.5)
# No need to add_child or start — it auto-plays
```

### Node Renames
| Godot 3 | Godot 4 |
|---------|---------|
| `KinematicBody2D` | `CharacterBody2D` |
| `KinematicBody` | `CharacterBody3D` |
| `RigidBody` | `RigidBody3D` |
| `StaticBody` | `StaticBody3D` |
| `Area` | `Area3D` |
| `Spatial` | `Node3D` |
| `Position2D` | `Marker2D` |
| `Position3D` | `Marker3D` |
| `YSort` | `Node2D` (with y_sort_enabled) |
| `Navigation2DServer` | `NavigationServer2D` |
| `VisualServer` | `RenderingServer` |
| `AudioServer.get_bus_layout()` | Different API |

### Method Renames
| Godot 3 | Godot 4 |
|---------|---------|
| `instance()` | `instantiate()` |
| `move_and_slide(velocity)` | `velocity = ...; move_and_slide()` |
| `is_on_floor()` (after move_and_slide) | Same, but velocity is now a property |
| `get_slide_count()` | `get_slide_collision_count()` |
| `get_slide_collision()` | Same |
| `yield(obj, "signal")` | `await obj.signal` |
| `rand_range()` | `randf_range()` |
| `stepify()` | `snapped()` |
| `str2var()` | `str_to_var()` |
| `var2str()` | `var_to_str()` |
| `update()` | `queue_redraw()` |
| `get_world_2d()` | `get_world_2d()` (same) |
| `.rect_position` | `.position` (Control) |
| `.rect_size` | `.size` (Control) |
| `.rect_min_size` | `.custom_minimum_size` (Control) |

### CharacterBody2D Movement
```gdscript
# Godot 3
func _physics_process(delta):
    var velocity = Vector2.ZERO
    velocity = move_and_slide(velocity, Vector2.UP)

# Godot 4
func _physics_process(delta: float) -> void:
    velocity = Vector2.ZERO  # velocity is now a built-in property
    move_and_slide()  # Uses self.velocity automatically
    # is_on_floor() etc. still work the same way
```

### Export Syntax
```gdscript
# Godot 3
export(int) var health = 100
export(float, 0, 1, 0.01) var opacity = 1.0
export(String, "Sword", "Bow") var weapon = "Sword"
export(PackedScene) var enemy_scene

# Godot 4
@export var health: int = 100
@export_range(0.0, 1.0, 0.01) var opacity: float = 1.0
@export_enum("Sword", "Bow") var weapon: String = "Sword"
@export var enemy_scene: PackedScene
```

### Shader Changes
```glsl
// Godot 3
SCREEN_TEXTURE  // Built-in

// Godot 4
uniform sampler2D screen_texture : hint_screen_texture;
// Must declare as uniform, not built-in
```

### GDExtension (replaces GDNative)
- GDNative is completely removed in Godot 4
- GDExtension is the new C/C++ binding system
- Different API, different build system
- Extensions are more tightly integrated with the engine

---

## Top 15 GDScript Mistakes

### 1. Uncached Node References in _process()
```gdscript
# BAD: Tree traversal every frame
func _process(delta: float) -> void:
    $Sprite2D.rotation += delta
    get_node("UI/HealthBar").value = health

# GOOD: Cache with @onready
@onready var sprite: Sprite2D = $Sprite2D
@onready var health_bar: ProgressBar = $UI/HealthBar

func _process(delta: float) -> void:
    sprite.rotation += delta
    health_bar.value = health
```

### 2. Setting Position Before add_child()
```gdscript
# BAD: No parent transform yet
var bullet := bullet_scene.instantiate()
bullet.global_position = muzzle.global_position  # Wrong!
get_tree().current_scene.add_child(bullet)

# GOOD: Set position AFTER add_child
var bullet := bullet_scene.instantiate()
get_tree().current_scene.add_child(bullet)
bullet.global_position = muzzle.global_position  # Correct!
```

### 3. Using get_parent() (Upward Coupling)
```gdscript
# BAD: Child knows about parent
func take_damage(amount: int) -> void:
    health -= amount
    if health <= 0:
        get_parent().enemy_killed(self)  # Fragile!

# GOOD: Signal up
signal died

func take_damage(amount: int) -> void:
    health -= amount
    if health <= 0:
        died.emit()
```

### 4. Duplicate Signal Connections
```gdscript
# BAD: Connect every frame or without checking
func _process(delta: float) -> void:
    button.pressed.connect(_on_pressed)  # Duplicates!

# GOOD: Connect once in _ready, or guard
func _ready() -> void:
    button.pressed.connect(_on_pressed)

# Or guard:
if not button.pressed.is_connected(_on_pressed):
    button.pressed.connect(_on_pressed)
```

### 5. Physics in _process() Instead of _physics_process()
```gdscript
# BAD: Variable framerate physics
func _process(delta: float) -> void:
    velocity.y += gravity * delta
    move_and_slide()

# GOOD: Fixed-rate physics
func _physics_process(delta: float) -> void:
    velocity.y += gravity * delta
    move_and_slide()
```

### 6. Not Using Static Typing
```gdscript
# BAD: Untyped = slow + no error catching
var speed = 200
var items = []

# GOOD: Typed = fast + IDE support
var speed: float = 200.0
var items: Array[ItemData] = []
```

### 7. Awaiting Signals from Freed Nodes
```gdscript
# BAD: Hangs forever if enemy is freed
await enemy.died  # If enemy.queue_free() was called, this never resolves

# GOOD: Check validity
if is_instance_valid(enemy):
    await enemy.died
```

### 8. Modifying Resource Shared Across Instances
```gdscript
# BAD: Changing a shared resource affects all users
@export var stats: CharacterStats  # Shared .tres file
func take_damage(amount: int) -> void:
    stats.health -= amount  # Changes it for ALL enemies!

# GOOD: Duplicate on ready
func _ready() -> void:
    stats = stats.duplicate()
```

### 9. Using String Comparisons for State
```gdscript
# BAD: Typos are silent bugs
if state == "atack":  # Misspelled, never true
    attack()

# GOOD: Use enums
enum State { IDLE, WALK, ATTACK }
if state == State.ATTACK:
    attack()
```

### 10. Forgetting call_deferred() in Physics Callbacks
```gdscript
# BAD: Modifying physics state during physics step
func _on_body_entered(body: Node) -> void:
    body.queue_free()  # May crash or produce warnings
    add_child(explosion)  # Unsafe during physics

# GOOD: Defer modifications
func _on_body_entered(body: Node) -> void:
    body.queue_free()  # queue_free is actually safe (it's deferred by design)
    add_child.call_deferred(explosion)  # Defer adding nodes
```

### 11. Overusing Autoloads
```gdscript
# BAD: Everything is a global singleton
# GameManager, PlayerManager, EnemyManager, UIManager,
# AudioManager, InputManager, SceneManager, SaveManager...

# GOOD: Only truly global state
# GameManager (score, settings)
# EventBus (global signals)
# SceneManager (scene transitions)
# Everything else belongs in scenes
```

### 12. Monolithic Scripts
```gdscript
# BAD: 500-line player.gd handling everything
# Movement, combat, inventory, dialogue, animation, sound...

# GOOD: Component scenes
# Player.tscn with:
# - MovementComponent.tscn
# - CombatComponent.tscn
# - InventoryComponent.tscn
```

### 13. Not Using Scenes for Reusable Behaviors
```gdscript
# BAD: Duplicating health logic in every enemy script

# GOOD: HealthComponent.tscn — one scene, used everywhere
```

### 14. Ignoring the Errors Tab
The Errors tab in the debugger shows connection failures, null references, and type mismatches that don't crash but produce wrong behavior. Check it regularly.

### 15. Over-Engineering with Design Patterns
```gdscript
# BAD: Full state machine for a chest that opens/closes
# BAD: Object pool when you spawn 3 bullets per game
# BAD: ECS architecture replacing Godot's node system

# GOOD: Use patterns when complexity warrants them
# A boolean is fine for open/close
# Object pool when spawning 100+ objects per second
# Godot's node system IS the component system
```

---

## Performance Pitfalls

### Common Performance Killers
1. **Untyped GDScript** — 40%+ slower than statically typed
2. **$Node in _process()** — Tree traversal every frame
3. **Creating nodes every frame** — Use object pooling
4. **Too many draw calls** — Batch with CanvasGroup or Y-sort
5. **Physics bodies for non-physics objects** — Use Area2D for triggers
6. **Complex collision shapes** — Use simple shapes, combine with multiple
7. **GDScript for heavy computation** — Use C# or GDExtension for math-heavy code
8. **Unoptimized shaders** — Minimize texture samples, avoid `discard`
9. **Signals with many connections** — Each connection is a dictionary lookup

### Profiling
```gdscript
# Built-in profiler: Debugger > Profiler tab

# Manual timing
var start := Time.get_ticks_msec()
# ... expensive operation ...
var elapsed := Time.get_ticks_msec() - start
print("Operation took %d ms" % elapsed)

# Performance monitors
Performance.get_monitor(Performance.TIME_FPS)
Performance.get_monitor(Performance.OBJECT_NODE_COUNT)
Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
```

---

## Debugging Techniques

### Breakpoints
Click the gutter (left margin) in the script editor to set breakpoints. While paused:
- Inspect local, member, and global variables
- Step through code line by line
- Modify variable values live

### Remote Scene Tree
Run the game, then click the "Remote" tab in the Scene dock to inspect the live scene tree. Verify nodes exist, check property values, and debug visibility issues.

### Print Debugging
```gdscript
# Basic
print("health: ", health)

# Formatted
print("Player at %s with %d HP" % [global_position, health])

# Push errors/warnings (show in Errors tab)
push_error("Invalid state: %s" % state)
push_warning("Health below zero, clamping")

# Debug draw
func _draw() -> void:
    draw_circle(Vector2.ZERO, detection_radius, Color(1, 0, 0, 0.3))
    # Call queue_redraw() when data changes
```

### Assertions
```gdscript
# Debug-only assertions
assert(health >= 0, "Health should never be negative")
assert(weapon != null, "Weapon must be assigned")
# Stripped from release builds
```

### Debug Overlay
```gdscript
# Quick debug label
func _process(delta: float) -> void:
    if OS.is_debug_build():
        $DebugLabel.text = "FPS: %d\nPos: %s\nState: %s" % [
            Engine.get_frames_per_second(),
            global_position,
            State.keys()[current_state]
        ]
```

---

## LLM-Specific Pitfalls

Common mistakes made by LLMs when generating GDScript code:

### Signal Callback Naming
When connecting signals in GDScript, match the exact callback name from the `.tscn` file:
```gdscript
# If .tscn has: signal = "area_entered" method = "_on_area_entered"
# CORRECT:
func _on_area_entered(area):

# WRONG (don't prefix with node name):
func _on_area_2d_area_entered(area):
```
Always check the `.tscn` scene file for existing signal connections before writing callbacks. The editor auto-generates names as `_on_<NodeName>_<signal>`, but many projects use shorter names.

### Autoload Singleton Access
Autoloaded singletons (configured in project.godot) are globally accessible by name:
```gdscript
# CORRECT — access directly:
QuestManager.progress_quest(quest_id, step_id)
QuestManager.step_updated.connect(_on_step_updated)

# WRONG — unnecessary variable:
@onready var quest_manager = get_node("/root/QuestManager")

# WRONG — never instantiate autoloads:
var qm = preload("res://addons/quest_manager/QuestManager.gd").new()
```

### Preserving Existing Values
When rewriting a file to add functionality, preserve ALL existing values:
```gdscript
# If the original has:
@export var speed := 600.0

# WRONG — don't change values that aren't part of the task:
@export var speed: float = 400.0

# CORRECT — keep the original value:
@export var speed := 600.0
```

### Use Project Constants, Not Invented IDs
Read `.tres` resource files and existing scripts to discover correct identifiers:
```gdscript
# WRONG — invented IDs:
QuestManager.progress_quest("shoot_em_up_quest", "kill")

# CORRECT — use IDs from the project:
const QUEST_ID := "shoot_em_up"
const STEP_ID := "kill_step"
QuestManager.progress_quest(QUEST_ID, STEP_ID)
```

### Empty Function Bodies
Every function MUST have at least one executable statement. A function with only a comment causes a GDScript parse error:
```gdscript
# WRONG — parse error:
func _ready():
    # Just a comment

# CORRECT:
func _ready():
    pass  # No logic needed yet
```

### Don't Add Unnecessary Boilerplate
Don't add defensive code for framework-provided nodes:
```gdscript
# WRONG — unnecessary null check for autoload:
if is_instance_valid(quest_manager):
    quest_manager.do_thing()

# CORRECT — autoloads are always valid:
QuestManager.do_thing()
```

### Tab Indentation (CRITICAL)
Godot 4 GDScript **requires tab indentation**. Space-indented scripts silently fail to parse — no error message, the script just doesn't load, causing 600s timeouts.
```gdscript
# WRONG — spaces (invisible failure):
func _ready():
    var x = 1        # 4 spaces — Godot rejects silently

# CORRECT — tabs:
func _ready():
	var x = 1        # tab character — Godot parses correctly
```
**This is the #1 root cause of Godot test timeouts.** Always use tabs, never spaces.

### Python-isms in GDScript
GDScript looks like Python but is NOT Python. These Python constructs do NOT exist:
```gdscript
# WRONG — Python syntax that doesn't exist in GDScript:
for i, card in enumerate(cards):     # No enumerate()
text = "Hello {}".format(name)       # No .format()
length = len(array)                  # No len()
items.sort(key=lambda x: x.name)     # No key= parameter
string.join(array)                   # Wrong syntax

# CORRECT — GDScript equivalents:
for i in range(cards.size()):        # Manual index loop
	var card = cards[i]
text = "Hello %s" % name             # % operator
length = array.size()                # .size() method
items.sort_custom(func(a, b): return a.name < b.name)  # sort_custom
var result = ", ".join(PackedStringArray(array))  # Static join
```

### Variant Type Inference with `:=`
The `:=` operator infers the type from the right side. When the right side returns `Variant` (e.g., `Array.pop_front()`, `Dictionary.get()`), Godot cannot infer the type and throws a parse error.
```gdscript
# WRONG — parse error (pop_front returns Variant):
var card := cards.pop_front()
var value := dict.get("key")

# CORRECT — use `=` (untyped) or explicit type:
var card = cards.pop_front()
var value = dict.get("key")
# Or with explicit cast:
var card: Card = cards.pop_front() as Card
```

### _to_string() Trailing Newline
GDScript's string interpolation with `+` or `%` can add trailing newlines that break test assertions. Use `PackedStringArray` + `", ".join()` for clean output:
```gdscript
# WRONG — may have trailing newline or inconsistent spacing:
func _to_string() -> String:
	var result = ""
	for card in cards:
		result += card.name + ", "
	return result.trim_suffix(", ")

# CORRECT — clean, predictable output:
func _to_string() -> String:
	var parts := PackedStringArray()
	for card in cards:
		parts.append(card.name)
	return ", ".join(parts)
```

### Protected File Modification
Never modify files not explicitly mentioned in the task instruction. Common mistake: adding signals/exports to `player.gd` to "help" other scripts communicate:
```gdscript
# WRONG — modifying player.gd to add quest-related signals:
# In player.gd (NOT part of the task):
signal quest_failed(quest_name)  # Added undefined variable quest_name
func _on_hp_zero():
    quest_failed.emit(quest_name)  # quest_name not defined — crash!

# CORRECT — implement quest failure in quest_ui.gd (the task target):
func _process(delta):
    if player.hp == 0 and state == State.RUNNING:
        quest.failed = true
```
Only read unmentioned files for context. Never write to them.

### .tscn Property Omission
When adding UI nodes to .tscn files, LLMs forget essential Control properties. Always include:
```
# Label nodes — always set:
horizontal_alignment = 1    # 0=left, 1=center, 2=right
vertical_alignment = 1      # 0=top, 1=center, 2=bottom
anchors_preset = 8          # 8=center, 5=center-bottom, etc.

# All Control nodes — set layout:
offset_left = -100
offset_top = -20
offset_right = 100
offset_bottom = 20

# Inside containers — always set:
layout_mode = 2             # Required inside HBox/VBox/GridContainer
```

### .tscn Scene Modification Safety
When modifying an existing .tscn file, **keep ALL existing content** and only ADD new nodes/resources. Never rewrite the entire file:
```
# WRONG approach:
1. Read file
2. Rewrite entire file from memory (loses nodes, breaks hierarchy)

# CORRECT approach:
1. Read file
2. Add new [ext_resource] entries (update load_steps count)
3. Add new [sub_resource] entries
4. Add new [node] entries with correct parent paths
5. Add new [connection] entries at the end
6. Keep every existing line unchanged
```

### Don't Rename Existing Functions
If a .tscn file has `method="_on_retry_pressed"`, the GDScript must define exactly `func _on_retry_pressed()`. Never rename it:
```gdscript
# .tscn has: [connection signal="pressed" from="Retry" to="." method="_on_retry_pressed"]

# WRONG — renamed:
func _on_pressed():
    pass

# CORRECT — matches .tscn exactly:
func _on_retry_pressed():
    pass
```

---

## Editor Gotchas

1. **Saved scenes don't update instances** — If you change a reusable scene, existing instances may not reflect the change until you re-open them
2. **Inherited scenes** — Changes to the base scene propagate, but overridden properties in child scenes are preserved
3. **Scene unique names (%)** — Must be manually set per node; they don't propagate to inherited scenes
4. **Tool scripts** — Guard all game logic with `Engine.is_editor_hint()` or they'll run in the editor
5. **.import folder** — Auto-generated, don't edit or version control
6. **.godot folder** — Contains cached imports, don't version control
7. **UID conflicts** — If you copy .tscn/.tres files manually, UIDs may conflict. Let the editor handle duplication
