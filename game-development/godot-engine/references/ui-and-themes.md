# UI System & Themes

## Table of Contents
1. [Control Node Hierarchy](#control-node-hierarchy)
2. [Container Layout](#container-layout)
3. [Anchors & Margins](#anchors--margins)
4. [Theme System](#theme-system)
5. [Common UI Patterns](#common-ui-patterns)
6. [Input Focus & Navigation](#input-focus--navigation)
7. [Responsive Design](#responsive-design)

---

## Control Node Hierarchy

All UI nodes inherit from `Control`. Key node types:

| Node | Purpose |
|------|---------|
| `Label` | Display text |
| `RichTextLabel` | Formatted text with BBCode |
| `Button` | Clickable button |
| `TextureButton` | Image-based button |
| `LineEdit` | Single-line text input |
| `TextEdit` | Multi-line text input |
| `ProgressBar` | Progress indicator |
| `TextureRect` | Display images |
| `Panel` | Background panel |
| `ScrollContainer` | Scrollable area |
| `TabContainer` | Tabbed pages |
| `ItemList` | Selectable item list |
| `Tree` | Hierarchical data display |
| `SpinBox` | Numeric input with arrows |
| `HSlider` / `VSlider` | Slider controls |
| `CheckBox` / `CheckButton` | Boolean toggles |
| `OptionButton` | Dropdown selection |
| `ColorPickerButton` | Color selection |

---

## Container Layout

Containers automatically arrange child Controls. Never manually position children inside a container — it will be overridden.

### HBoxContainer / VBoxContainer
```
# Horizontal layout
HBoxContainer
├── Button "Play"
├── Button "Options"
└── Button "Quit"

# Vertical layout
VBoxContainer
├── Label "Settings"
├── HSlider "Volume"
└── Button "Back"
```

### GridContainer
```gdscript
# Grid with 3 columns (set in inspector or code)
var grid := GridContainer.new()
grid.columns = 3
for i in 9:
    var btn := Button.new()
    btn.text = str(i + 1)
    grid.add_child(btn)
```

### MarginContainer
Adds padding around a single child.

### CenterContainer
Centers its child.

### Size Flags
Control how children behave inside containers:

```gdscript
# Expand to fill available space
button.size_flags_horizontal = Control.SIZE_EXPAND_FILL

# Shrink to minimum size (default)
button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN

# Stretch ratio (relative sizing)
panel_a.size_flags_stretch_ratio = 2.0  # Gets 2x the space
panel_b.size_flags_stretch_ratio = 1.0  # Gets 1x the space
```

### PanelContainer
Draws a background behind its child. Good for cards, dialogs.

### AspectRatioContainer
Maintains child's aspect ratio.

---

## Anchors & Margins

Anchors define how a Control is positioned relative to its parent. Values range from 0 (left/top) to 1 (right/bottom).

### Common Anchor Presets
```gdscript
# Full screen
control.set_anchors_preset(Control.PRESET_FULL_RECT)

# Top-left corner
control.set_anchors_preset(Control.PRESET_TOP_LEFT)

# Center
control.set_anchors_preset(Control.PRESET_CENTER)

# Bottom bar (full width, bottom)
control.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)

# Right side (full height, right edge)
control.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
```

### Manual Anchor Setting
```gdscript
# Health bar in top-left with 10px margin
health_bar.anchor_left = 0.0
health_bar.anchor_top = 0.0
health_bar.anchor_right = 0.0
health_bar.anchor_bottom = 0.0
health_bar.offset_left = 10
health_bar.offset_top = 10
health_bar.offset_right = 210  # 200px wide
health_bar.offset_bottom = 30   # 20px tall
```

---

## Theme System

Themes control the visual style of all Control nodes. They cascade down the tree — a theme set on a parent applies to all children.

### Creating a Theme in Code
```gdscript
var theme := Theme.new()

# Font
var font := load("res://fonts/main_font.tres") as Font
theme.set_font("font", "Label", font)
theme.set_font_size("font_size", "Label", 16)

# Colors
theme.set_color("font_color", "Label", Color.WHITE)
theme.set_color("font_color", "Button", Color(0.9, 0.9, 0.9))
theme.set_color("font_hover_color", "Button", Color.WHITE)

# StyleBoxes (backgrounds)
var btn_normal := StyleBoxFlat.new()
btn_normal.bg_color = Color(0.2, 0.2, 0.3)
btn_normal.corner_radius_top_left = 4
btn_normal.corner_radius_top_right = 4
btn_normal.corner_radius_bottom_left = 4
btn_normal.corner_radius_bottom_right = 4
btn_normal.content_margin_left = 12
btn_normal.content_margin_right = 12
btn_normal.content_margin_top = 8
btn_normal.content_margin_bottom = 8
theme.set_stylebox("normal", "Button", btn_normal)

var btn_hover := btn_normal.duplicate()
btn_hover.bg_color = Color(0.3, 0.3, 0.4)
theme.set_stylebox("hover", "Button", btn_hover)

var btn_pressed := btn_normal.duplicate()
btn_pressed.bg_color = Color(0.15, 0.15, 0.25)
theme.set_stylebox("pressed", "Button", btn_pressed)

# Apply to root UI node
$UIRoot.theme = theme
```

### Theme Overrides (Per-Node)
```gdscript
# Override just one property without creating a whole theme
label.add_theme_color_override("font_color", Color.RED)
label.add_theme_font_size_override("font_size", 24)

# Check if override exists
if label.has_theme_color_override("font_color"):
    label.remove_theme_color_override("font_color")
```

---

## Common UI Patterns

### Health Bar
```gdscript
# health_bar.gd
extends ProgressBar

func update_display(current: int, maximum: int) -> void:
    max_value = maximum
    value = current
    # Tween for smooth animation
    var tween := create_tween()
    tween.tween_property(self, "value", float(current), 0.3)
```

### Dialog Box
```gdscript
# dialog_box.gd
extends PanelContainer

signal dialog_closed

@onready var label: RichTextLabel = %DialogLabel
@onready var continue_indicator: TextureRect = %ContinueIndicator

var _full_text: String = ""
var _char_index: int = 0
var _typing: bool = false

func show_dialog(text: String) -> void:
    _full_text = text
    _char_index = 0
    label.text = ""
    visible = true
    _typing = true
    continue_indicator.visible = false

func _process(delta: float) -> void:
    if not _typing:
        return
    _char_index += 1
    label.text = _full_text.substr(0, _char_index)
    if _char_index >= _full_text.length():
        _typing = false
        continue_indicator.visible = true

func _unhandled_input(event: InputEvent) -> void:
    if not visible:
        return
    if event.is_action_pressed("ui_accept"):
        if _typing:
            # Skip to end
            label.text = _full_text
            _typing = false
            continue_indicator.visible = true
        else:
            visible = false
            dialog_closed.emit()
        get_viewport().set_input_as_handled()
```

### Inventory Grid
```gdscript
# inventory_ui.gd
extends GridContainer

@export var slot_scene: PackedScene

func display_inventory(items: Array[ItemData]) -> void:
    # Clear existing
    for child in get_children():
        child.queue_free()
    # Populate
    for item in items:
        var slot: InventorySlot = slot_scene.instantiate()
        add_child(slot)
        slot.set_item(item)
```

### Pause Menu
```gdscript
# pause_menu.gd
extends CanvasLayer

func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("pause"):
        toggle_pause()
        get_viewport().set_input_as_handled()

func toggle_pause() -> void:
    var is_paused: bool = not get_tree().paused
    get_tree().paused = is_paused
    visible = is_paused
    # This node must have process_mode = PROCESS_MODE_ALWAYS
```

---

## Input Focus & Navigation

### Keyboard/Gamepad Navigation
```gdscript
# Set focus neighbors for gamepad navigation
button_play.focus_neighbor_bottom = button_options.get_path()
button_options.focus_neighbor_top = button_play.get_path()
button_options.focus_neighbor_bottom = button_quit.get_path()
button_quit.focus_neighbor_top = button_options.get_path()

# Grab initial focus
button_play.grab_focus()
```

### Mouse Filter
```gdscript
# Control.MOUSE_FILTER_STOP — handles mouse events (default for buttons)
# Control.MOUSE_FILTER_PASS — handles then passes to parent
# Control.MOUSE_FILTER_IGNORE — transparent to mouse

# Make a Label not block clicks
label.mouse_filter = Control.MOUSE_FILTER_IGNORE
```

---

## .tscn UI Property Checklist

When adding UI nodes to `.tscn` files, these properties are frequently forgotten by LLMs but required for correct rendering. Always set them explicitly.

### Label Properties
```
[node name="ScoreLabel" type="Label" parent="."]
# ALWAYS set these for Labels:
horizontal_alignment = 1    # 0=left, 1=center, 2=right
vertical_alignment = 1      # 0=top, 1=center, 2=bottom

# Position via anchors (pick one preset):
anchors_preset = 1          # 0=top-left, 1=top-right, 5=center-left
                            # 7=center-right, 8=center, 12=full-rect

# Fine-tune with offsets (pixels from anchor point):
offset_left = -200
offset_top = 10
offset_right = -20
offset_bottom = 40

# Text content:
text = "Score: 0"
```

### Common anchors_preset Values
| Value | Position | Use Case |
|-------|----------|----------|
| 0 | Top-Left | Default, HUD scores |
| 1 | Top-Right | Timer, ammo count |
| 2 | Bottom-Left | Chat, inventory |
| 3 | Bottom-Right | Minimap |
| 5 | Center-Left | Side panel |
| 7 | Center-Right | Side panel |
| 8 | Center | Dialog, popup |
| 10 | Top-Wide | Header bar |
| 12 | Full-Rect | Background, overlay |
| 14 | Bottom-Wide | Status bar |
| 15 | Left-Wide | Sidebar |

### Control Nodes Inside Containers
```
# CRITICAL: Inside HBox/VBox/Grid containers, ALWAYS set:
layout_mode = 2             # Required — tells Godot this is container-managed

# TextureRect inside container:
[node name="Heart1" type="TextureRect" parent="."]
layout_mode = 2
texture = ExtResource("2_heart")
stretch_mode = 5            # 5 = keep aspect ratio centered
```

### CanvasLayer HUD Pattern
```
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/hud.gd" id="1_scr"]

[node name="HUD" type="CanvasLayer"]
script = ExtResource("1_scr")

[node name="ScoreLabel" type="Label" parent="."]
anchors_preset = 1          # top-right
anchor_left = 1.0
anchor_right = 1.0
offset_left = -200
offset_right = -20
offset_bottom = 40
horizontal_alignment = 2    # right-aligned text
text = "Score: 0"

[node name="HealthBar" type="ProgressBar" parent="."]
anchors_preset = 0          # top-left
offset_left = 20
offset_top = 10
offset_right = 220
offset_bottom = 30
value = 100.0
```

### Common Mistakes in .tscn UI
1. **Missing `horizontal_alignment`** on Labels — text defaults to left even when centered layout is needed
2. **Missing `anchors_preset`** — node appears at (0,0) instead of intended position
3. **Missing `layout_mode = 2`** inside containers — node ignores container layout
4. **Wrong `offset` signs** — offsets are relative to anchor, right/bottom offsets are often negative for top-right positioning
5. **Forgetting `anchor_left/right/top/bottom`** with preset — preset sets anchors, but manual anchor values override

---

## Responsive Design

### Stretch Settings (project.godot)
```ini
[display]
window/size/viewport_width=1920
window/size/viewport_height=1080
window/stretch/mode="canvas_items"  # or "viewport"
window/stretch/aspect="keep"        # or "expand", "keep_width", "keep_height"
```

- `canvas_items` — UI scales, 2D pixel art stays sharp
- `viewport` — Everything scales (good for pixel art games)
- `keep` — Adds black bars to maintain aspect ratio
- `expand` — No black bars, content may stretch

### Dynamic Font Sizing
```gdscript
func _ready() -> void:
    get_viewport().size_changed.connect(_on_viewport_resized)

func _on_viewport_resized() -> void:
    var viewport_width: float = get_viewport_rect().size.x
    var scale_factor: float = viewport_width / 1920.0
    var font_size: int = int(16 * scale_factor)
    label.add_theme_font_size_override("font_size", font_size)
```
