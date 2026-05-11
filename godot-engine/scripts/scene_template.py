#!/usr/bin/env python3
"""Generate .tscn scene files from predefined templates.

Creates properly formatted Godot 4.x scene files with common node setups
for player characters, enemies, UI screens, and levels.

Usage:
    python scene_template.py <template> <name> [--output <path>] [--script]

Templates:
    player    CharacterBody2D with Sprite2D, CollisionShape2D, AnimationPlayer
    enemy     CharacterBody2D with AI-ready structure (detection area, state label)
    ui        Control root with common UI layout (MarginContainer + VBoxContainer)
    level     Node2D with TileMapLayer, camera, and spawn markers
    component Reusable Node with signal-based interface
"""

import argparse
import sys
import uuid
from pathlib import Path


def _uid() -> str:
    """Generate a Godot-style UID."""
    return uuid.uuid4().hex[:12]


# ── Templates ────────────────────────────────────────────────────────

def player_scene(name: str, with_script: bool) -> tuple[str, str | None]:
    uid = _uid()
    script_section = ""
    script_attach = ""
    script_content = None

    if with_script:
        script_section = (
            f'\n[ext_resource type="Script" path="res://{name.lower()}.gd" id="1"]\n'
        )
        script_attach = '\nscript = ExtResource("1")'
        script_content = f"""\
extends CharacterBody2D
class_name {name}

@export var speed: float = 200.0
@export var acceleration: float = 800.0
@export var friction: float = 600.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var collision: CollisionShape2D = $CollisionShape2D
@onready var anim_player: AnimationPlayer = $AnimationPlayer


func _physics_process(delta: float) -> void:
\tvar input: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")

\tif input != Vector2.ZERO:
\t\tvelocity = velocity.move_toward(input * speed, acceleration * delta)
\telse:
\t\tvelocity = velocity.move_toward(Vector2.ZERO, friction * delta)

\tmove_and_slide()
"""

    load_steps = 2 if with_script else 1
    tscn = f"""\
[gd_scene load_steps={load_steps} format=3 uid="uid://{uid}"]
{script_section}
[sub_resource type="RectangleShape2D" id="SubResource_1"]
size = Vector2(16, 32)

[node name="{name}" type="CharacterBody2D"]{script_attach}

[node name="Sprite2D" type="Sprite2D" parent="."]

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("SubResource_1")

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
"""
    return tscn, script_content


def enemy_scene(name: str, with_script: bool) -> tuple[str, str | None]:
    uid = _uid()
    script_section = ""
    script_attach = ""
    script_content = None

    if with_script:
        script_section = (
            f'\n[ext_resource type="Script" path="res://{name.lower()}.gd" id="1"]\n'
        )
        script_attach = '\nscript = ExtResource("1")'
        script_content = f"""\
extends CharacterBody2D
class_name {name}

signal died

@export var speed: float = 80.0
@export var max_health: int = 50

var health: int = max_health

@onready var sprite: Sprite2D = $Sprite2D
@onready var detection_area: Area2D = $DetectionArea


func _ready() -> void:
\thealth = max_health
\tdetection_area.body_entered.connect(_on_body_entered_detection)
\tdetection_area.body_exited.connect(_on_body_exited_detection)


func take_damage(amount: int) -> void:
\thealth -= amount
\tif health <= 0:
\t\tdie()


func die() -> void:
\tdied.emit()
\tqueue_free()


func _on_body_entered_detection(body: Node2D) -> void:
\tpass  # Start chasing


func _on_body_exited_detection(body: Node2D) -> void:
\tpass  # Return to patrol
"""

    load_steps = 3 if with_script else 2
    tscn = f"""\
[gd_scene load_steps={load_steps} format=3 uid="uid://{uid}"]
{script_section}
[sub_resource type="RectangleShape2D" id="SubResource_1"]
size = Vector2(16, 16)

[sub_resource type="CircleShape2D" id="SubResource_2"]
radius = 120.0

[node name="{name}" type="CharacterBody2D"]{script_attach}

[node name="Sprite2D" type="Sprite2D" parent="."]

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("SubResource_1")

[node name="DetectionArea" type="Area2D" parent="."]

[node name="DetectionShape" type="CollisionShape2D" parent="DetectionArea"]
shape = SubResource("SubResource_2")
"""
    return tscn, script_content


def ui_scene(name: str, with_script: bool) -> tuple[str, str | None]:
    uid = _uid()
    script_section = ""
    script_attach = ""
    script_content = None

    if with_script:
        script_section = (
            f'\n[ext_resource type="Script" path="res://{name.lower()}.gd" id="1"]\n'
        )
        script_attach = '\nscript = ExtResource("1")'
        script_content = f"""\
extends Control
class_name {name}


func _ready() -> void:
\tpass


func _unhandled_input(event: InputEvent) -> void:
\tif event.is_action_pressed("ui_cancel"):
\t\t_on_back_pressed()


func _on_back_pressed() -> void:
\tpass  # Navigate back or close
"""

    load_steps = 2 if with_script else 1
    tscn = f"""\
[gd_scene load_steps={load_steps} format=3 uid="uid://{uid}"]
{script_section}
[node name="{name}" type="Control"]{script_attach}
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2

[node name="MarginContainer" type="MarginContainer" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
theme_override_constants/margin_left = 20
theme_override_constants/margin_top = 20
theme_override_constants/margin_right = 20
theme_override_constants/margin_bottom = 20

[node name="VBoxContainer" type="VBoxContainer" parent="MarginContainer"]
layout_mode = 2

[node name="TitleLabel" type="Label" parent="MarginContainer/VBoxContainer"]
layout_mode = 2
text = "{name}"
horizontal_alignment = 1
"""
    return tscn, script_content


def level_scene(name: str, with_script: bool) -> tuple[str, str | None]:
    uid = _uid()
    script_section = ""
    script_attach = ""
    script_content = None

    if with_script:
        script_section = (
            f'\n[ext_resource type="Script" path="res://{name.lower()}.gd" id="1"]\n'
        )
        script_attach = '\nscript = ExtResource("1")'
        script_content = f"""\
extends Node2D
class_name {name}

@onready var player_spawn: Marker2D = $PlayerSpawn
@onready var camera: Camera2D = $Camera2D


func _ready() -> void:
\tpass  # Spawn player at player_spawn.global_position
"""

    load_steps = 2 if with_script else 1
    tscn = f"""\
[gd_scene load_steps={load_steps} format=3 uid="uid://{uid}"]
{script_section}
[node name="{name}" type="Node2D"]{script_attach}

[node name="TileMapLayer" type="TileMapLayer" parent="."]

[node name="Camera2D" type="Camera2D" parent="."]
position = Vector2(640, 360)

[node name="PlayerSpawn" type="Marker2D" parent="."]
position = Vector2(100, 300)

[node name="Entities" type="Node2D" parent="."]
"""
    return tscn, script_content


def component_scene(name: str, with_script: bool) -> tuple[str, str | None]:
    uid = _uid()
    script_section = ""
    script_attach = ""
    script_content = None

    if with_script:
        script_section = (
            f'\n[ext_resource type="Script" path="res://{name.lower()}.gd" id="1"]\n'
        )
        script_attach = '\nscript = ExtResource("1")'
        script_content = f"""\
extends Node
class_name {name}
## Reusable component. Attach as a child scene to any entity.

signal value_changed(new_value: int)
signal depleted

@export var max_value: int = 100
var current_value: int = max_value


func _ready() -> void:
\tcurrent_value = max_value


func decrease(amount: int) -> void:
\tcurrent_value = max(0, current_value - amount)
\tvalue_changed.emit(current_value)
\tif current_value <= 0:
\t\tdepleted.emit()


func increase(amount: int) -> void:
\tcurrent_value = min(max_value, current_value + amount)
\tvalue_changed.emit(current_value)


func reset() -> void:
\tcurrent_value = max_value
\tvalue_changed.emit(current_value)
"""

    load_steps = 2 if with_script else 1
    tscn = f"""\
[gd_scene load_steps={load_steps} format=3 uid="uid://{uid}"]
{script_section}
[node name="{name}" type="Node"]{script_attach}
"""
    return tscn, script_content


TEMPLATES = {
    "player": player_scene,
    "enemy": enemy_scene,
    "ui": ui_scene,
    "level": level_scene,
    "component": component_scene,
}


# ── CLI ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Godot 4.x .tscn scene files from templates."
    )
    parser.add_argument("template", choices=TEMPLATES.keys(),
                        help="Scene template type")
    parser.add_argument("name", help="Scene/class name in PascalCase (e.g. Player, Slime, MainMenu)")
    parser.add_argument("--output", "-o", default=".",
                        help="Output directory (default: current dir)")
    parser.add_argument("--script", "-s", action="store_true",
                        help="Also generate a matching .gd script file")

    args = parser.parse_args()
    name = args.name
    out_dir = Path(args.output).resolve()

    if not name[0].isupper():
        print(f"Warning: Godot class names should be PascalCase. Got '{name}'.", file=sys.stderr)

    if not out_dir.exists():
        out_dir.mkdir(parents=True)

    template_fn = TEMPLATES[args.template]
    tscn_content, script_content = template_fn(name, args.script)

    # Write .tscn
    tscn_path = out_dir / f"{name.lower()}.tscn"
    tscn_path.write_text(tscn_content, encoding="utf-8")
    print(f"Created {tscn_path}")

    # Write .gd
    if args.script and script_content:
        gd_path = out_dir / f"{name.lower()}.gd"
        gd_path.write_text(script_content, encoding="utf-8")
        print(f"Created {gd_path}")


if __name__ == "__main__":
    main()
