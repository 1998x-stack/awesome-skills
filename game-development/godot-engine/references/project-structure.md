# Project Structure & Organization

## Table of Contents
1. [Recommended Directory Layout](#recommended-directory-layout)
2. [Naming Conventions](#naming-conventions)
3. [Scene Organization](#scene-organization)
4. [Save/Load System](#saveload-system)
5. [Input Handling](#input-handling)
6. [Audio Management](#audio-management)
7. [Export & Build](#export--build)
8. [Version Control](#version-control)
9. [Testing](#testing)

---

## Recommended Directory Layout

```
project_root/
├── project.godot
├── .gitignore
├── export_presets.cfg
│
├── scenes/
│   ├── main.tscn                 # Entry point
│   ├── levels/
│   │   ├── level_01.tscn
│   │   └── level_02.tscn
│   ├── entities/
│   │   ├── player/
│   │   │   ├── player.tscn
│   │   │   └── player.gd
│   │   └── enemies/
│   │       ├── slime.tscn
│   │       └── skeleton.tscn
│   ├── ui/
│   │   ├── hud.tscn
│   │   ├── main_menu.tscn
│   │   ├── pause_menu.tscn
│   │   └── settings_menu.tscn
│   └── components/
│       ├── health_component.tscn
│       ├── hitbox_component.tscn
│       └── state_machine.tscn
│
├── scripts/
│   ├── autoloads/
│   │   ├── game_manager.gd
│   │   ├── event_bus.gd
│   │   ├── scene_manager.gd
│   │   └── audio_manager.gd
│   ├── resources/
│   │   ├── weapon_data.gd
│   │   └── character_stats.gd
│   └── utils/
│       └── math_utils.gd
│
├── resources/
│   ├── weapons/
│   │   ├── sword.tres
│   │   └── bow.tres
│   ├── enemies/
│   │   ├── slime_stats.tres
│   │   └── skeleton_stats.tres
│   └── themes/
│       └── game_theme.tres
│
├── assets/
│   ├── sprites/
│   │   ├── player/
│   │   ├── enemies/
│   │   ├── tiles/
│   │   └── ui/
│   ├── audio/
│   │   ├── music/
│   │   └── sfx/
│   ├── fonts/
│   └── shaders/
│
└── addons/                       # Third-party plugins
    └── plugin_name/
```

### Small Project Variant
For small games/prototypes, flatten the structure:
```
project_root/
├── project.godot
├── main.tscn
├── player.tscn / player.gd
├── enemy.tscn / enemy.gd
├── hud.tscn / hud.gd
├── game_manager.gd (autoload)
├── sprites/
├── audio/
└── shaders/
```

### Co-locate Script and Scene
Keep `.gd` files next to their `.tscn` files. This is the most common Godot convention:
```
entities/player/
├── player.tscn
├── player.gd
├── player_states/
│   ├── idle_state.gd
│   ├── run_state.gd
│   └── jump_state.gd
└── player_sprite.png
```

---

## Naming Conventions

### Files
| Type | Convention | Example |
|------|-----------|---------|
| Scenes | `snake_case.tscn` | `main_menu.tscn` |
| Scripts | `snake_case.gd` | `player_controller.gd` |
| Resources | `snake_case.tres` | `sword_data.tres` |
| Shaders | `snake_case.gdshader` | `dissolve_effect.gdshader` |
| Images | `snake_case.png` | `player_idle.png` |
| Audio | `snake_case.wav/.ogg` | `jump_sound.wav` |

### GDScript
| Element | Convention | Example |
|---------|-----------|---------|
| Classes | `PascalCase` | `class_name PlayerController` |
| Functions | `snake_case` | `func get_damage()` |
| Variables | `snake_case` | `var max_health: int` |
| Constants | `UPPER_SNAKE_CASE` | `const MAX_SPEED: float` |
| Enums | `PascalCase` (type), `UPPER_SNAKE_CASE` (values) | `enum State { IDLE, WALKING }` |
| Signals | `snake_case` (past tense) | `signal health_changed` |
| Private members | `_prefixed` | `var _internal_state: int` |
| Node references | `snake_case` | `@onready var health_bar` |
| Callback methods | `_on_` prefix | `func _on_button_pressed()` |

---

## Scene Organization

### Scene Tree Conventions
- Root node type matches the entity's role (CharacterBody2D for player, Control for UI)
- Name root node after the entity (Player, MainMenu, HUD)
- Group related nodes under organizational Node2D/Node3D parents
- Use scene-unique names (%) for nodes referenced in code

### When to Make Something a Scene
- It's reused in multiple places → Scene
- It's complex enough to edit independently → Scene
- It represents a complete game entity → Scene
- It's a simple, one-off child node → Keep inline

---

## Save/Load System

### Using ConfigFile (Simple)
```gdscript
# save_manager.gd (autoload)
extends Node

const SAVE_PATH := "user://savegame.cfg"

func save_game(data: Dictionary) -> void:
    var config := ConfigFile.new()
    for key in data:
        config.set_value("game", key, data[key])
    config.save(SAVE_PATH)

func load_game() -> Dictionary:
    var config := ConfigFile.new()
    var err := config.load(SAVE_PATH)
    if err != OK:
        return {}
    var data := {}
    for key in config.get_section_keys("game"):
        data[key] = config.get_value("game", key)
    return data

func has_save() -> bool:
    return FileAccess.file_exists(SAVE_PATH)

func delete_save() -> void:
    if has_save():
        DirAccess.remove_absolute(SAVE_PATH)
```

### Using JSON (Complex Data)
```gdscript
func save_to_json(data: Dictionary) -> void:
    var json_string := JSON.stringify(data, "\t")
    var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    file.store_string(json_string)

func load_from_json() -> Dictionary:
    if not FileAccess.file_exists(SAVE_PATH):
        return {}
    var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
    var json := JSON.new()
    var error := json.parse(file.get_as_text())
    if error != OK:
        push_error("JSON parse error: %s" % json.get_error_message())
        return {}
    return json.data as Dictionary
```

### Using Resources (Type-Safe)
```gdscript
# save_data.gd
class_name SaveData
extends Resource

@export var player_position: Vector2
@export var player_health: int
@export var inventory: Array[String]
@export var level_id: int
@export var play_time: float

# Save
func save_game(data: SaveData) -> void:
    ResourceSaver.save(data, "user://savegame.tres")

# Load
func load_game() -> SaveData:
    if ResourceLoader.exists("user://savegame.tres"):
        return ResourceLoader.load("user://savegame.tres") as SaveData
    return SaveData.new()
```

---

## Input Handling

### Input Map (project.godot)
Define actions in Project Settings > Input Map, then use them in code:

```gdscript
# Checking input
func _physics_process(delta: float) -> void:
    var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    velocity = direction * speed

func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("jump"):
        jump()
    if event.is_action_pressed("attack"):
        attack()
```

### Input Priority
```
_input()              # First — for global shortcuts
_gui_input()          # UI elements (buttons, etc.)
_shortcut_input()     # Shortcuts
_unhandled_key_input() # Unhandled keyboard
_unhandled_input()    # Last — for gameplay input
```

### Consuming Input
```gdscript
func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("interact"):
        interact()
        get_viewport().set_input_as_handled()  # Prevent propagation
```

### Rebindable Input
```gdscript
func rebind_action(action: String, event: InputEvent) -> void:
    InputMap.action_erase_events(action)
    InputMap.action_add_event(action, event)
```

---

## Audio Management

```gdscript
# audio_manager.gd (autoload)
extends Node

@onready var music_player: AudioStreamPlayer = $MusicPlayer
@onready var sfx_pool: Array[AudioStreamPlayer] = []

func _ready() -> void:
    # Create SFX pool
    for i in 8:
        var player := AudioStreamPlayer.new()
        player.bus = "SFX"
        add_child(player)
        sfx_pool.append(player)

func play_music(stream: AudioStream, fade_duration: float = 0.5) -> void:
    if music_player.stream == stream and music_player.playing:
        return
    # Crossfade
    var tween := create_tween()
    tween.tween_property(music_player, "volume_db", -40.0, fade_duration)
    await tween.finished
    music_player.stream = stream
    music_player.play()
    tween = create_tween()
    tween.tween_property(music_player, "volume_db", 0.0, fade_duration)

func play_sfx(stream: AudioStream, volume_db: float = 0.0) -> void:
    for player in sfx_pool:
        if not player.playing:
            player.stream = stream
            player.volume_db = volume_db
            player.play()
            return
    push_warning("SFX pool exhausted")
```

### Audio Buses
Set up in Project Settings > Audio:
```
Master
├── Music
├── SFX
│   ├── UI
│   └── Ambient
└── Voice
```

---

## Export & Build

### Export Presets
Configure in Project > Export for each target platform:
- **Windows** — .exe + .pck
- **macOS** — .app bundle or .dmg
- **Linux** — .x86_64
- **Web** — .html + .wasm + .pck
- **Android** — .apk or .aab
- **iOS** — Xcode project

### Command-Line Export
```bash
# Export for Windows
godot --headless --export-release "Windows" build/game.exe

# Export for Web
godot --headless --export-release "Web" build/index.html

# Export debug build
godot --headless --export-debug "Windows" build/game_debug.exe
```

### Custom Export Settings
```ini
# export_presets.cfg
[preset.0]
name="Windows Desktop"
platform="Windows Desktop"
custom_features=""
export_filter="all_resources"
```

---

## Version Control

### .gitignore for Godot
```gitignore
# Godot 4 specific
.godot/

# Godot-generated import files
*.import

# Mono/C# specific
.mono/
data_*/
mono_crash.*.json

# Export builds
build/
export/

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/
*.code-workspace
```

### What to Commit
- `project.godot` — Always
- `.tscn`, `.tres`, `.gd` files — Always
- `export_presets.cfg` — Usually (may contain signing keys — check)
- Asset files (`.png`, `.wav`, etc.) — Always
- `.godot/` directory — Never (auto-generated)
- `addons/` — Yes, commit third-party addons

---

## Testing

### GUT (Godot Unit Testing)
```gdscript
# tests/test_health_component.gd
extends GutTest

var health_comp: HealthComponent

func before_each() -> void:
    health_comp = HealthComponent.new()
    health_comp.max_health = 100
    add_child(health_comp)

func after_each() -> void:
    health_comp.queue_free()

func test_initial_health() -> void:
    assert_eq(health_comp.current_health, 100)

func test_take_damage() -> void:
    health_comp.take_damage(30)
    assert_eq(health_comp.current_health, 70)

func test_cannot_go_below_zero() -> void:
    health_comp.take_damage(150)
    assert_eq(health_comp.current_health, 0)

func test_died_signal() -> void:
    watch_signals(health_comp)
    health_comp.take_damage(100)
    assert_signal_emitted(health_comp, "died")
```

### Headless Testing
```bash
# Run GUT tests from command line
godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests -gexit

# Run specific test
godot --headless -s addons/gut/gut_cmdln.gd -gtest=res://tests/test_health.gd -gexit
```

### Scene Testing (Godot built-in)
```gdscript
# test_scene.gd — attached to a test scene that runs assertions
extends Node

func _ready() -> void:
    var player := preload("res://scenes/player.tscn").instantiate()
    add_child(player)

    # Test movement
    player.velocity = Vector2(100, 0)
    player.move_and_slide()
    assert(player.global_position.x > 0, "Player should have moved right")

    print("All tests passed!")
    get_tree().quit(0)
```
