# Godot 4 .tscn Scene File Format Reference

## File Structure (sections appear in this order)

```
[gd_scene load_steps=N format=3 uid="uid://xxxxx"]

[ext_resource type="Type" uid="uid://xxx" path="res://path" id="string_id"]

[sub_resource type="Type" id="string_id"]
property = value

[node name="Name" type="Type" parent="."]
property = value

[connection signal="sig" from="NodePath" to="." method="_on_callback"]
```

## 1. Header

```
[gd_scene load_steps=5 format=3 uid="uid://cbqmq7k0v3k84"]
```
- `load_steps` = count of ext_resource + sub_resource declarations
- `format=3` — ALWAYS use 3 for Godot 4 (format=2 is Godot 3)

## 2. External Resources

```
[ext_resource type="Script" uid="uid://xxx" path="res://scripts/player.gd" id="1_juomx"]
[ext_resource type="Texture2D" path="res://assets/sprite.png" id="2_abc"]
```

**CRITICAL — Godot 4 vs Godot 3:**
| Godot 4 (correct) | Godot 3 (WRONG) |
|---|---|
| `id="1_abc"` (quoted string) | `id=1` (bare integer) |
| `ExtResource("1_abc")` | `ExtResource(1)` |
| `SubResource("Shape_1")` | `SubResource(1)` |
| `type="Texture2D"` | `type="Texture"` |
| `type="CompressedTexture2D"` | `type="StreamTexture"` |

Common types: `Script`, `Texture2D`, `CompressedTexture2D`, `FontFile`, `PackedScene`

## 3. Sub-Resources (inline resources)

```
[sub_resource type="CircleShape2D" id="CircleShape2D_abc"]
radius = 20.0

[sub_resource type="RectangleShape2D" id="RectShape_1"]
size = Vector2(6, 3)

[sub_resource type="AtlasTexture" id="Atlas_1"]
atlas = ExtResource("1_tex")
region = Rect2(0, 480, 299, 240)
```

Common types: `CircleShape2D`, `RectangleShape2D`, `CapsuleShape2D`, `AtlasTexture`, `SpriteFrames`, `Animation`, `AnimationLibrary`, `Environment`, `Sky`

## 4. Nodes

Root node (no parent attribute):
```
[node name="Player" type="CharacterBody2D"]
script = ExtResource("1_script")
```

Child nodes (parent = path from root):
```
[node name="Sprite" type="Sprite2D" parent="."]
texture = ExtResource("2_tex")
position = Vector2(10, 0)

[node name="Shape" type="CollisionShape2D" parent="."]
shape = SubResource("CircleShape2D_abc")

[node name="Deep" type="Node2D" parent="Container/Sub"]
```

## 5. Connections (always at end of file)

```
[connection signal="pressed" from="Button" to="." method="_on_button_pressed"]
[connection signal="area_entered" from="HitBox" to="." method="_on_hit_box_area_entered"]
[connection signal="timeout" from="Timer" to="." method="_on_timer_timeout"]
```

## Property Value Syntax

```gdscript
# Vectors
position = Vector2(100, 200)
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)

# Colors
modulate = Color(1, 0, 0, 1)

# Rects
region_rect = Rect2(0, 0, 64, 64)

# References
script = ExtResource("1_abc")
shape = SubResource("Shape_1")

# StringName (for animation names, library keys)
animation = &"idle"

# NodePath
tracks/0/path = NodePath("Sprite:frame")

# Typed arrays
PackedFloat32Array(0, 0.1, 0.2)
PackedVector2Array(Vector2(0, 0), Vector2(1, 1))

# Booleans
visible = true
region_enabled = false
```

## Common Patterns

### Area2D with collision (bullet, hitbox):
```
[gd_scene load_steps=3 format=3]

[ext_resource type="Script" path="res://scripts/bullet.gd" id="1_scr"]

[sub_resource type="RectangleShape2D" id="RectShape_1"]
size = Vector2(6, 3)

[node name="Bullet" type="Area2D"]
collision_layer = 16
collision_mask = 44
script = ExtResource("1_scr")

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("RectShape_1")

[node name="Sprite2D" type="Sprite2D" parent="."]
texture = ExtResource("2_tex")

[connection signal="area_entered" from="." to="." method="_on_area_entered"]
[connection signal="body_entered" from="." to="." method="_on_body_entered"]
```

### UI scene (HUD, health bar):
```
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/hud.gd" id="1_scr"]

[node name="HUD" type="CanvasLayer"]
script = ExtResource("1_scr")

[node name="ScoreLabel" type="Label" parent="."]
anchors_preset = 1
anchor_left = 1.0
anchor_right = 1.0
offset_left = -200.0
offset_right = -20.0
offset_bottom = 40.0
horizontal_alignment = 2
text = "Score: 0"
```

### HBoxContainer with TextureRects:
```
[node name="HeartBar" type="HBoxContainer"]
custom_minimum_size = Vector2(281, 45)
theme_override_constants/separation = 5
script = ExtResource("1_scr")

[node name="Heart1" type="TextureRect" parent="."]
layout_mode = 2
texture = ExtResource("2_heart")
stretch_mode = 5
```

### AnimationPlayer with library:
```
[sub_resource type="Animation" id="Anim_idle"]
resource_name = "idle"
length = 0.2
loop_mode = 1
tracks/0/type = "value"
tracks/0/path = NodePath("Sprite:frame")
tracks/0/interp = 1
tracks/0/loop_wrap = true
tracks/0/keys = {
"times": PackedFloat32Array(0, 0.1),
"transitions": PackedFloat32Array(1, 1),
"update": 1,
"values": [0, 1]
}

[sub_resource type="AnimationLibrary" id="AnimLib_1"]
_data = {
&"idle": SubResource("Anim_idle")
}

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
libraries = {
&"": SubResource("AnimLib_1")
}
```

## Rules When Editing .tscn Files

1. **Always READ the file first** before modifying
2. **Keep ALL existing content** — only ADD new nodes/resources
3. **Update load_steps** when adding ext_resource or sub_resource
4. **No inline comments** — Godot does not support `# comment` on property lines
5. **Connections go at the END** after all nodes
6. **Use Godot 4 syntax** — quoted string IDs, format=3
7. **Collision layers are bitmasks** — layer 1=1, layer 2=2, layer 3=4, layer 5=16
