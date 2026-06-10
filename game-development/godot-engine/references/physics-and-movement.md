# Godot 4.x Physics & Movement Reference

## Table of Contents

- [CharacterBody2D / CharacterBody3D](#characterbody2d--characterbody3d)
  - [Basic move_and_slide](#basic-move_and_slide)
  - [Floor Detection](#floor-detection)
  - [Slopes](#slopes)
  - [One-Way Platforms](#one-way-platforms)
  - [Moving Platforms](#moving-platforms)
- [RigidBody2D / RigidBody3D](#rigidbody2d--rigidbody3d)
  - [Forces vs Impulses](#forces-vs-impulses)
  - [Sleeping and Freeze Modes](#sleeping-and-freeze-modes)
  - [Custom Integrator](#custom-integrator)
- [Area2D / Area3D](#area2d--area3d)
  - [Body Enter/Exit Signals](#body-enterexit-signals)
  - [Area Enter/Exit Signals](#area-enterexit-signals)
  - [Overlap Detection (Manual Query)](#overlap-detection-manual-query)
  - [Gravity Zones](#gravity-zones)
- [Collision Layers and Masks](#collision-layers-and-masks)
  - [Concept: Layer vs Mask](#concept-layer-vs-mask)
  - [Setting via Code](#setting-via-code)
  - [Naming Conventions](#naming-conventions)
- [Raycasts](#raycasts)
  - [RayCast2D / RayCast3D Node](#raycast2d--raycast3d-node)
  - [Direct Space Queries (PhysicsDirectSpaceState)](#direct-space-queries-physicsdirectspacestate)
- [ShapeCasts](#shapecasts)
  - [ShapeCast2D / ShapeCast3D Node](#shapecast2d--shapecast3d-node)
  - [Ground and Wall Detection with ShapeCast](#ground-and-wall-detection-with-shapecast)
- [Common Movement Patterns](#common-movement-patterns)
  - [Platformer](#platformer)
  - [Top-Down (4-directional)](#top-down-4-directional)
  - [8-Directional with Smooth Acceleration](#8-directional-with-smooth-acceleration)
  - [Smooth Acceleration / Deceleration Helper](#smooth-acceleration--deceleration-helper)
- [Physics Material](#physics-material)
  - [PhysicsMaterial Resource](#physicsmaterial-resource)
  - [Per-Body Overrides](#per-body-overrides)

---

## CharacterBody2D / CharacterBody3D

`CharacterBody2D` and `CharacterBody3D` are kinematic bodies moved via code. They do **not** respond to physics forces automatically. Movement is driven by setting `velocity` then calling `move_and_slide()`.

### Basic move_and_slide

```gdscript
# 2D example
extends CharacterBody2D

@export var speed: float = 200.0

func _physics_process(delta: float) -> void:
    var direction: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")
    velocity = direction * speed
    move_and_slide()
```

```gdscript
# 3D example
extends CharacterBody3D

@export var speed: float = 5.0

func _physics_process(delta: float) -> void:
    var input_dir: Vector2 = Input.get_vector("move_left", "move_right", "move_forward", "move_back")
    var direction: Vector3 = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()

    velocity.x = direction.x * speed
    velocity.z = direction.z * speed

    move_and_slide()
```

**Key points:**
- `move_and_slide()` uses and mutates `velocity` directly (no return value in Godot 4).
- Always call in `_physics_process()`, not `_process()`.
- Collision responses (sliding) are computed automatically.

### Floor Detection

```gdscript
extends CharacterBody2D

@export var speed: float = 200.0
@export var jump_velocity: float = -400.0
@export var gravity: float = 980.0

func _physics_process(delta: float) -> void:
    # Apply gravity when not on floor
    if not is_on_floor():
        velocity.y += gravity * delta

    # Jump only when grounded
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity

    var direction: float = Input.get_axis("move_left", "move_right")
    velocity.x = direction * speed

    move_and_slide()
```

**Detection methods available after `move_and_slide()`:**
| Method | Returns | Purpose |
|---|---|---|
| `is_on_floor()` | `bool` | Standing on a surface within `floor_max_angle` |
| `is_on_wall()` | `bool` | Touching a wall (surface steeper than `floor_max_angle`) |
| `is_on_ceiling()` | `bool` | Head hit a ceiling |
| `get_floor_normal()` | `Vector2/3` | Normal of the floor surface |
| `get_floor_angle()` | `float` | Angle of the floor (radians from up direction) |
| `get_last_motion()` | `Vector2/3` | Actual motion applied last frame |
| `get_slide_collision_count()` | `int` | Number of collisions during last slide |
| `get_slide_collision(idx)` | `KinematicCollision2D/3D` | Collision info at index |
| `get_last_slide_collision()` | `KinematicCollision2D/3D` | Most recent collision |

### Slopes

```gdscript
extends CharacterBody2D

@export var speed: float = 200.0
@export var gravity: float = 980.0

func _ready() -> void:
    # Max angle (in radians) a surface can have and still count as "floor"
    # Default is ~45 degrees. For steeper slopes:
    floor_max_angle = deg_to_rad(50.0)

    # Snap to floor when walking down slopes (prevents bouncing)
    floor_snap_length = 8.0

    # Stop on slopes when not moving (prevents sliding down)
    floor_stop_on_slope = true

    # Use constant speed on slopes (don't slow down going uphill)
    floor_constant_speed = true

    # Block sliding on floor when standing still
    floor_block_on_wall = true

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y += gravity * delta

    var direction: float = Input.get_axis("move_left", "move_right")
    velocity.x = direction * speed

    move_and_slide()
```

### One-Way Platforms

One-way platforms let the character pass through from below and land on top.

**Scene setup:**
1. Create a `StaticBody2D` with a `CollisionShape2D`.
2. On the `CollisionShape2D`, enable **One Way Collision** in the inspector.

```gdscript
# Or set it via code:
func _ready() -> void:
    var collision_shape: CollisionShape2D = $CollisionShape2D
    collision_shape.one_way_collision = true
    collision_shape.one_way_collision_margin = 4.0  # tolerance in pixels
```

**Drop-through one-way platforms:**

```gdscript
extends CharacterBody2D

@export var speed: float = 200.0
@export var gravity: float = 980.0
@export var jump_velocity: float = -400.0

var _drop_through_timer: float = 0.0

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y += gravity * delta

    # Drop through one-way platform
    if Input.is_action_just_pressed("move_down") and is_on_floor():
        # Temporarily disable collision with the platform
        _drop_through_timer = 0.2
        position.y += 2.0  # nudge past the platform

    if _drop_through_timer > 0.0:
        _drop_through_timer -= delta
        # While dropping, the floor snap won't pull us back
        floor_snap_length = 0.0
    else:
        floor_snap_length = 8.0

    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity

    velocity.x = Input.get_axis("move_left", "move_right") * speed
    move_and_slide()
```

### Moving Platforms

**Method 1: AnimatableBody2D (preferred for simple paths)**

The platform moves via `AnimationPlayer` or code. `CharacterBody2D` automatically rides it when `floor_stop_on_slope` and platform sync are enabled.

```gdscript
# MovingPlatform.gd -- attach to AnimatableBody2D
extends AnimatableBody2D

@export var travel: Vector2 = Vector2(0, -128)
@export var duration: float = 2.0

var _elapsed: float = 0.0

func _physics_process(delta: float) -> void:
    _elapsed += delta
    var weight: float = (sin(_elapsed * TAU / duration) + 1.0) / 2.0
    var target_pos: Vector2 = Vector2.ZERO.lerp(travel, weight)
    # sync_to_physics ensures CharacterBody2D riders move smoothly
    global_position = position + target_pos
```

**Method 2: Manually apply platform velocity**

```gdscript
# On the CharacterBody2D riding the platform
extends CharacterBody2D

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y += 980.0 * delta
    else:
        # get_platform_velocity() returns the velocity of the floor we stand on
        var platform_vel: Vector2 = get_platform_velocity()
        velocity += platform_vel * delta  # optional: add to our own velocity

    velocity.x = Input.get_axis("move_left", "move_right") * 200.0
    move_and_slide()
```

---

## RigidBody2D / RigidBody3D

`RigidBody2D/3D` are fully physics-driven. The engine handles gravity, collisions, and responses. You influence them through forces and impulses.

### Forces vs Impulses

```gdscript
extends RigidBody2D

@export var thrust: float = 500.0
@export var jump_impulse: float = 300.0

func _physics_process(delta: float) -> void:
    # --- FORCES (continuous, accumulated over time) ---
    # apply_central_force: adds force at center of mass (no torque)
    if Input.is_action_pressed("move_right"):
        apply_central_force(Vector2(thrust, 0))

    # apply_force: adds force at an offset (causes torque/rotation)
    # Second arg is offset from center of mass
    if Input.is_action_pressed("thrust_corner"):
        apply_force(Vector2(0, -thrust), Vector2(10, 0))

    # apply_torque: rotational force
    var torque_dir: float = Input.get_axis("rotate_left", "rotate_right")
    apply_torque(torque_dir * 1000.0)

    # --- IMPULSES (instant, one-frame velocity change) ---
    # apply_central_impulse: instant velocity change at center
    if Input.is_action_just_pressed("jump"):
        apply_central_impulse(Vector2(0, -jump_impulse))

    # apply_impulse: instant velocity change at offset (causes spin)
    if Input.is_action_just_pressed("kick"):
        apply_impulse(Vector2(100, -50), Vector2(0, 10))

    # apply_torque_impulse: instant angular velocity change
    if Input.is_action_just_pressed("spin"):
        apply_torque_impulse(500.0)
```

**Force vs Impulse summary:**
| Method | Duration | Use case |
|---|---|---|
| `apply_central_force()` | Continuous (call every frame) | Engines, thrusters, wind |
| `apply_force()` | Continuous + offset | Asymmetric thrust, steering |
| `apply_torque()` | Continuous rotation | Motors, spinning |
| `apply_central_impulse()` | Instant (call once) | Jump, explosion knockback |
| `apply_impulse()` | Instant + offset | Hit at a specific point |
| `apply_torque_impulse()` | Instant rotation | Sudden spin |

**Directly setting velocity (use sparingly):**

```gdscript
# In _integrate_forces for safe direct state manipulation
func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
    # Clamp max speed
    if state.linear_velocity.length() > 500.0:
        state.linear_velocity = state.linear_velocity.normalized() * 500.0

    # Or set velocity directly
    state.linear_velocity = Vector2(200, 0)
    state.angular_velocity = 0.0
```

### Sleeping and Freeze Modes

```gdscript
extends RigidBody2D

func _ready() -> void:
    # --- SLEEPING ---
    # When a body stops moving, it "sleeps" to save CPU.
    can_sleep = true              # allow sleeping (default true)
    sleeping = false              # force wake or sleep

    # Signal when sleep state changes
    sleeping_state_changed.connect(_on_sleeping_state_changed)

    # --- FREEZE MODES ---
    # freeze = true stops the body from moving entirely
    freeze = false

    # FREEZE_MODE_STATIC: behaves like StaticBody2D (others bounce off it)
    freeze_mode = RigidBody2D.FREEZE_MODE_STATIC

    # FREEZE_MODE_KINEMATIC: behaves like AnimatableBody2D
    # (can be moved via code and push other bodies)
    freeze_mode = RigidBody2D.FREEZE_MODE_KINEMATIC

func _on_sleeping_state_changed() -> void:
    if sleeping:
        print("Body fell asleep")
    else:
        print("Body woke up")

# Example: freeze an object when player picks it up
func pick_up() -> void:
    freeze_mode = RigidBody2D.FREEZE_MODE_KINEMATIC
    freeze = true

func drop() -> void:
    freeze = false
```

**RigidBody2D/3D properties reference:**

| Property | Type | Default | Purpose |
|---|---|---|---|
| `mass` | `float` | `1.0` | Mass in kg |
| `gravity_scale` | `float` | `1.0` | Multiplier on gravity (`0` = no gravity) |
| `linear_damp` | `float` | `0.0` | Linear velocity damping (air resistance) |
| `angular_damp` | `float` | `0.0` | Angular velocity damping |
| `continuous_cd` | `CCD` | `DISABLED` | Continuous collision detection mode |
| `max_contacts_reported` | `int` | `0` | How many contacts to report (must be >0 for `body_entered`) |
| `contact_monitor` | `bool` | `false` | Enable contact signals (requires `max_contacts_reported > 0`) |

### Custom Integrator

Override the default physics step for full control:

```gdscript
extends RigidBody2D

func _ready() -> void:
    custom_integrator = true

func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
    # Custom gravity
    var custom_gravity: Vector2 = Vector2(0, 400)
    state.linear_velocity += custom_gravity * state.step

    # Custom damping
    state.linear_velocity *= 0.99

    # Access contacts
    for i: int in range(state.get_contact_count()):
        var contact_pos: Vector2 = state.get_contact_local_position(i)
        var contact_normal: Vector2 = state.get_contact_local_normal(i)
        var collider: Object = state.get_contact_collider_object(i)
        print("Hit %s at %s" % [collider.name, contact_pos])
```

---

## Area2D / Area3D

`Area2D/3D` detect overlaps without causing physical collision responses. Used for triggers, pickups, damage zones, gravity fields.

### Body Enter/Exit Signals

```gdscript
# HitZone.gd -- attach to Area2D
extends Area2D

func _ready() -> void:
    # Fires when a PhysicsBody2D (CharacterBody2D, RigidBody2D, StaticBody2D) enters
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node2D) -> void:
    if body.is_in_group("player"):
        print("Player entered the zone")
        body.take_damage(10)

func _on_body_exited(body: Node2D) -> void:
    if body.is_in_group("player"):
        print("Player left the zone")
```

### Area Enter/Exit Signals

```gdscript
# Pickup.gd -- detects when player's hurtbox (another Area2D) overlaps
extends Area2D

func _ready() -> void:
    area_entered.connect(_on_area_entered)
    area_exited.connect(_on_area_exited)

func _on_area_entered(area: Area2D) -> void:
    if area.is_in_group("player_hurtbox"):
        collect()

func _on_area_entered(area: Area2D) -> void:
    pass  # handle exit if needed

func collect() -> void:
    # Process pickup logic
    queue_free()
```

### Overlap Detection (Manual Query)

```gdscript
# Check overlaps on demand instead of relying on signals
extends Area2D

func get_enemies_in_range() -> Array[Node2D]:
    var bodies: Array[Node2D] = []
    for body: Node2D in get_overlapping_bodies():
        if body.is_in_group("enemies"):
            bodies.append(body)
    return bodies

func get_overlapping_hitboxes() -> Array[Area2D]:
    var areas: Array[Area2D] = []
    for area: Area2D in get_overlapping_areas():
        if area.is_in_group("hitbox"):
            areas.append(area)
    return areas

func has_any_overlap() -> bool:
    return has_overlapping_bodies() or has_overlapping_areas()
```

**Important:** `get_overlapping_bodies()` and `get_overlapping_areas()` require `monitoring = true` (default). Results are only valid after the physics frame -- do not call in `_ready()`. Use `await get_tree().physics_frame` or call in `_physics_process()`.

### Gravity Zones

```gdscript
# GravityZone.gd -- Area2D with custom gravity
# In the inspector or code, configure the Area's gravity properties:
extends Area2D

func _ready() -> void:
    # Override gravity for bodies inside this area
    gravity_space_override = Area2D.SPACE_OVERRIDE_REPLACE
    gravity_direction = Vector2(0, -1)  # upward gravity
    gravity = 400.0

    # Other override modes:
    # SPACE_OVERRIDE_COMBINE       -- add to default gravity
    # SPACE_OVERRIDE_COMBINE_REPLACE -- add, then stop processing lower-priority areas
    # SPACE_OVERRIDE_REPLACE       -- replace default gravity
    # SPACE_OVERRIDE_REPLACE_COMBINE -- replace, then keep processing lower-priority

    # Priority: higher priority areas override lower ones
    priority = 10

    # Linear/angular damping overrides (for water zones, etc.)
    linear_damp_space_override = Area2D.SPACE_OVERRIDE_COMBINE
    linear_damp = 5.0  # slows bodies down (simulates water)
    angular_damp_space_override = Area2D.SPACE_OVERRIDE_COMBINE
    angular_damp = 3.0
```

**Water zone example:**

```gdscript
# WaterZone.gd
extends Area2D

@export var buoyancy_force: float = 600.0

func _ready() -> void:
    gravity_space_override = Area2D.SPACE_OVERRIDE_COMBINE
    gravity_direction = Vector2(0, -1)
    gravity = buoyancy_force
    linear_damp_space_override = Area2D.SPACE_OVERRIDE_COMBINE
    linear_damp = 4.0
```

---

## Collision Layers and Masks

### Concept: Layer vs Mask

**Layer = "What I am."** Mask = **"What I detect/collide with."**

A collision occurs when **object A's mask includes object B's layer** OR **object B's mask includes object A's layer**.

```
Layer 1: Player
Layer 2: Enemies
Layer 3: Environment
Layer 4: Pickups
Layer 5: Projectiles
Layer 6: Player Hurtbox
Layer 7: Enemy Hurtbox

Player CharacterBody2D:
  Layer: 1 (I am a Player)
  Mask:  2, 3 (I collide with Enemies and Environment)

Enemy CharacterBody2D:
  Layer: 2 (I am an Enemy)
  Mask:  1, 3 (I collide with Player and Environment)

Pickup Area2D:
  Layer: 4 (I am a Pickup)
  Mask:  1 (I detect the Player)

Player Hurtbox Area2D:
  Layer: 6 (I am a Player Hurtbox)
  Mask:  7 (I detect Enemy Hurtboxes)
```

### Setting via Code

```gdscript
extends CharacterBody2D

func _ready() -> void:
    # --- Bitfield approach (layers/masks are 32-bit bitmasks) ---
    # Set layer to only layer 1
    collision_layer = 1  # bit 1 = 0b0001

    # Set mask to layers 2 and 3
    collision_mask = (1 << 1) | (1 << 2)  # bits 2+3 = 0b0110

    # --- Per-bit approach (1-indexed!) ---
    # Enable layer 1
    set_collision_layer_value(1, true)
    # Disable layer 2
    set_collision_layer_value(2, false)

    # Enable mask bit 3
    set_collision_mask_value(3, true)
    # Disable mask bit 5
    set_collision_mask_value(5, false)
```

**For Area2D (separate monitoring properties):**

```gdscript
extends Area2D

func _ready() -> void:
    # What this area IS (so others can detect it)
    collision_layer = 1 << 3  # layer 4

    # What this area DETECTS
    collision_mask = 1 << 0   # layer 1

    # monitoring = true  -> this area detects others (fires area_entered, body_entered)
    # monitorable = true -> other areas can detect this area
    monitoring = true
    monitorable = true
```

### .tscn Bitmask Values

In `.tscn` files, `collision_layer` and `collision_mask` use integer bitmask values (NOT bit indices). This is a common LLM mistake:

```
# .tscn bitmask values (1-indexed layers, power-of-2 values):
# Layer 1 = 1    (2^0)
# Layer 2 = 2    (2^1)
# Layer 3 = 4    (2^2)
# Layer 4 = 8    (2^3)
# Layer 5 = 16   (2^4)
# Layer 6 = 32   (2^5)
# Layer 7 = 64   (2^6)
# Layer 8 = 128  (2^7)

# Combine with addition/OR:
# Layers 1+3 = 1+4 = 5
# Layers 2+5 = 2+16 = 18
# Layers 1+2+3 = 1+2+4 = 7

# Example: Bullet on layer 5, detects layers 2+3+6
[node name="Bullet" type="Area2D"]
collision_layer = 16       # layer 5 = 2^4 = 16
collision_mask = 38        # layers 2+3+6 = 2+4+32 = 38

# Example: Player on layer 1, collides with layers 2+3
[node name="Player" type="CharacterBody2D"]
collision_layer = 1        # layer 1
collision_mask = 6         # layers 2+3 = 2+4 = 6
```

### Common .tscn Collision Mistakes
1. Using layer INDEX instead of bitmask VALUE: `collision_layer = 5` means layers 1+3, NOT layer 5
2. Forgetting that layer 5 = 16 (not 5)
3. Using `collision_layer = 0` — object is on NO layer, nothing can detect it

### Naming Conventions

Set layer names in **Project Settings > General > Layer Names > 2D Physics** (or 3D Physics). This makes the inspector show names instead of numbers.

Recommended naming scheme:

```
Layer 1:  player
Layer 2:  enemy
Layer 3:  environment
Layer 4:  pickup
Layer 5:  projectile_player
Layer 6:  projectile_enemy
Layer 7:  hurtbox_player
Layer 8:  hurtbox_enemy
Layer 9:  trigger
Layer 10: interactable
```

---

## Raycasts

### RayCast2D / RayCast3D Node

Add as a child node. Enable it, set target position, and query results.

```gdscript
extends CharacterBody2D

@onready var ray: RayCast2D = $RayCast2D
# In the scene, RayCast2D has:
#   enabled = true
#   target_position = Vector2(0, 50)  (points downward)

func _physics_process(delta: float) -> void:
    if ray.is_colliding():
        var collider: Object = ray.get_collider()
        var point: Vector2 = ray.get_collision_point()
        var normal: Vector2 = ray.get_collision_normal()
        print("Hit %s at %s, normal %s" % [collider.name, point, normal])

    # Dynamically change the ray direction
    ray.target_position = Vector2(100, 0).rotated(rotation)

    # Force update (normally updates each physics frame)
    ray.force_raycast_update()

    # Exclude specific objects
    ray.add_exception(self)

    # Filter by collision mask (same system as bodies)
    ray.collision_mask = 0b0101  # only layers 1 and 3

    # Detect Area2D nodes too (off by default)
    ray.collide_with_areas = true
    ray.collide_with_bodies = true
```

**3D raycast with multiple results via `target_position`:**

```gdscript
extends CharacterBody3D

@onready var ray: RayCast3D = $RayCast3D

func _physics_process(_delta: float) -> void:
    if ray.is_colliding():
        var hit_point: Vector3 = ray.get_collision_point()
        var hit_normal: Vector3 = ray.get_collision_normal()
        var collider: Object = ray.get_collider()
        var collider_rid: RID = ray.get_collider_rid()
        var collider_shape: int = ray.get_collider_shape()
```

### Direct Space Queries (PhysicsDirectSpaceState)

For one-off raycasts without a node, or raycasts from arbitrary positions.

```gdscript
# 2D direct raycast
extends Node2D

func cast_ray(from: Vector2, to: Vector2) -> Dictionary:
    var space_state: PhysicsDirectSpaceState2D = get_world_2d().direct_space_state
    var query: PhysicsRayQueryParameters2D = PhysicsRayQueryParameters2D.create(from, to)

    # Optional filters
    query.collision_mask = 0b0011         # layers 1 and 2
    query.collide_with_areas = false
    query.collide_with_bodies = true
    query.exclude = [self.get_rid()]      # exclude self
    query.hit_from_inside = false         # don't detect if starting inside a shape

    var result: Dictionary = space_state.intersect_ray(query)
    # result is empty {} on miss, or:
    # {
    #   "position": Vector2,
    #   "normal": Vector2,
    #   "collider": Object,
    #   "collider_id": int,
    #   "rid": RID,
    #   "shape": int
    # }
    return result
```

```gdscript
# 3D direct raycast
extends Node3D

func cast_ray_3d(from: Vector3, to: Vector3) -> Dictionary:
    var space_state: PhysicsDirectSpaceState3D = get_world_3d().direct_space_state
    var query: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(from, to)
    query.collision_mask = 0xFFFFFFFF  # all layers
    query.collide_with_areas = true
    query.collide_with_bodies = true

    var result: Dictionary = space_state.intersect_ray(query)
    return result
```

**Other direct space queries:**

```gdscript
extends Node2D

func query_examples() -> void:
    var space: PhysicsDirectSpaceState2D = get_world_2d().direct_space_state

    # --- Point intersection: what's at this point? ---
    var point_params: PhysicsPointQueryParameters2D = PhysicsPointQueryParameters2D.new()
    point_params.position = Vector2(100, 200)
    point_params.collision_mask = 0xFFFFFFFF
    point_params.collide_with_areas = true
    point_params.collide_with_bodies = true
    var point_results: Array[Dictionary] = space.intersect_point(point_params, 32)
    # Each dict: { "collider", "collider_id", "rid", "shape" }

    # --- Shape intersection: what overlaps this shape? ---
    var shape_params: PhysicsShapeQueryParameters2D = PhysicsShapeQueryParameters2D.new()
    shape_params.shape = CircleShape2D.new()
    shape_params.shape.radius = 50.0
    shape_params.transform = Transform2D(0, Vector2(100, 200))
    shape_params.collision_mask = 0xFFFFFFFF
    var shape_results: Array[Dictionary] = space.intersect_shape(shape_params, 32)
    # Each dict: { "collider", "collider_id", "rid", "shape" }

    # --- Shape motion (sweep test): will this shape hit anything if moved? ---
    shape_params.motion = Vector2(200, 0)  # direction + distance
    var cast_results: Array[float] = space.cast_motion(shape_params)
    # Returns [safe_fraction, unsafe_fraction] (0.0 to 1.0)
    # safe_fraction = how far along motion before collision
```

---

## ShapeCasts

### ShapeCast2D / ShapeCast3D Node

`ShapeCast` sweeps a shape along a direction and reports all collisions. More robust than raycasts for detecting ground or walls because it uses a volume instead of a line.

```gdscript
extends CharacterBody2D

@onready var ground_cast: ShapeCast2D = $GroundShapeCast
# In the scene, ShapeCast2D has:
#   shape = RectangleShape2D (slightly narrower than player)
#   target_position = Vector2(0, 10)  (sweep downward)
#   enabled = true

func _physics_process(delta: float) -> void:
    if ground_cast.is_colliding():
        var collision_count: int = ground_cast.get_collision_count()
        for i: int in range(collision_count):
            var collider: Object = ground_cast.get_collider(i)
            var point: Vector2 = ground_cast.get_collision_point(i)
            var normal: Vector2 = ground_cast.get_collision_normal(i)
            print("Ground hit: %s at %s" % [collider.name, point])

    # Closest safe/unsafe fractions (0.0 to 1.0 along target_position)
    var safe: float = ground_cast.get_closest_collision_safe_fraction()
    var unsafe: float = ground_cast.get_closest_collision_unsafe_fraction()
```

### Ground and Wall Detection with ShapeCast

```gdscript
extends CharacterBody2D

@onready var ground_check: ShapeCast2D = $GroundCheck
@onready var wall_check_left: ShapeCast2D = $WallCheckLeft
@onready var wall_check_right: ShapeCast2D = $WallCheckRight
@onready var ceiling_check: ShapeCast2D = $CeilingCheck

# Scene setup:
# GroundCheck:     shape=RectangleShape2D(width=14, height=2), target_position=(0, 6)
# WallCheckLeft:   shape=RectangleShape2D(width=2, height=14), target_position=(-6, 0)
# WallCheckRight:  shape=RectangleShape2D(width=2, height=14), target_position=(6, 0)
# CeilingCheck:    shape=RectangleShape2D(width=14, height=2), target_position=(0, -6)

@export var speed: float = 200.0
@export var gravity: float = 980.0
@export var jump_velocity: float = -400.0
@export var wall_jump_velocity: Vector2 = Vector2(250.0, -350.0)

var _is_grounded: bool = false
var _is_on_left_wall: bool = false
var _is_on_right_wall: bool = false

func _physics_process(delta: float) -> void:
    # Use shapecasts for detection (more reliable than is_on_floor for edge cases)
    _is_grounded = ground_check.is_colliding()
    _is_on_left_wall = wall_check_left.is_colliding()
    _is_on_right_wall = wall_check_right.is_colliding()

    if not _is_grounded:
        velocity.y += gravity * delta

    # Wall jump
    if Input.is_action_just_pressed("jump"):
        if _is_grounded:
            velocity.y = jump_velocity
        elif _is_on_left_wall:
            velocity = Vector2(wall_jump_velocity.x, wall_jump_velocity.y)
        elif _is_on_right_wall:
            velocity = Vector2(-wall_jump_velocity.x, wall_jump_velocity.y)

    # Wall slide (slow fall when touching wall)
    if not _is_grounded and (_is_on_left_wall or _is_on_right_wall):
        velocity.y = minf(velocity.y, 50.0)

    velocity.x = Input.get_axis("move_left", "move_right") * speed
    move_and_slide()
```

**ShapeCast configuration tips:**
- Set `collision_mask` to match only relevant layers (e.g., environment only for ground checks).
- Set `max_results` if you only need the first collision (`max_results = 1`).
- Use `add_exception()` to ignore the parent body.
- Call `force_shapecast_update()` if you need results immediately after changing position.

---

## Common Movement Patterns

### Platformer

```gdscript
extends CharacterBody2D

@export_group("Movement")
@export var speed: float = 200.0
@export var acceleration: float = 1200.0
@export var friction: float = 1000.0

@export_group("Jump")
@export var jump_velocity: float = -350.0
@export var gravity: float = 980.0
@export var fall_gravity_multiplier: float = 1.5
@export var jump_cut_multiplier: float = 0.5
@export var coyote_time: float = 0.1
@export var jump_buffer_time: float = 0.1

var _coyote_timer: float = 0.0
var _jump_buffer_timer: float = 0.0
var _was_on_floor: bool = false

func _physics_process(delta: float) -> void:
    # --- Gravity ---
    if not is_on_floor():
        # Heavier gravity when falling (makes jumps feel snappier)
        var grav_mult: float = fall_gravity_multiplier if velocity.y > 0.0 else 1.0
        velocity.y += gravity * grav_mult * delta

    # --- Coyote time (grace period after leaving a ledge) ---
    if is_on_floor():
        _coyote_timer = coyote_time
    elif _was_on_floor:
        pass  # just left floor, timer already set
    _coyote_timer -= delta
    _was_on_floor = is_on_floor()

    # --- Jump buffer (press jump slightly before landing) ---
    if Input.is_action_just_pressed("jump"):
        _jump_buffer_timer = jump_buffer_time
    _jump_buffer_timer -= delta

    # --- Jump ---
    if _jump_buffer_timer > 0.0 and _coyote_timer > 0.0:
        velocity.y = jump_velocity
        _jump_buffer_timer = 0.0
        _coyote_timer = 0.0

    # --- Jump cut (release jump early for shorter hop) ---
    if Input.is_action_just_released("jump") and velocity.y < 0.0:
        velocity.y *= jump_cut_multiplier

    # --- Horizontal movement with acceleration ---
    var direction: float = Input.get_axis("move_left", "move_right")
    if direction != 0.0:
        velocity.x = move_toward(velocity.x, direction * speed, acceleration * delta)
    else:
        velocity.x = move_toward(velocity.x, 0.0, friction * delta)

    move_and_slide()
```

### Top-Down (4-directional)

```gdscript
extends CharacterBody2D

@export var speed: float = 150.0

func _physics_process(delta: float) -> void:
    var input: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")

    # For strict 4-directional, snap to dominant axis
    if abs(input.x) > abs(input.y):
        input.y = 0.0
    else:
        input.x = 0.0

    velocity = input.normalized() * speed
    move_and_slide()
```

### 8-Directional with Smooth Acceleration

```gdscript
extends CharacterBody2D

@export var max_speed: float = 200.0
@export var acceleration: float = 800.0
@export var friction: float = 600.0

func _physics_process(delta: float) -> void:
    var input: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")

    if input != Vector2.ZERO:
        # Accelerate toward input direction (normalized to prevent diagonal speed boost)
        velocity = velocity.move_toward(input.normalized() * max_speed, acceleration * delta)
    else:
        # Decelerate to zero
        velocity = velocity.move_toward(Vector2.ZERO, friction * delta)

    move_and_slide()
```

### Smooth Acceleration / Deceleration Helper

A reusable utility for any movement style:

```gdscript
class_name MovementHelper

## Smoothly approach a target velocity using acceleration and deceleration rates.
static func smooth_velocity(
    current: Vector2,
    target: Vector2,
    accel: float,
    decel: float,
    delta: float
) -> Vector2:
    var result: Vector2 = current
    # X axis
    if abs(target.x) > 0.01:
        result.x = move_toward(current.x, target.x, accel * delta)
    else:
        result.x = move_toward(current.x, 0.0, decel * delta)
    # Y axis
    if abs(target.y) > 0.01:
        result.y = move_toward(current.y, target.y, accel * delta)
    else:
        result.y = move_toward(current.y, 0.0, decel * delta)
    return result

## Exponential decay approach (feels "floaty" / smooth)
## factor is 0.0 (instant) to 1.0 (never reaches target)
## Typical values: 0.1 - 0.3
static func exp_decay(current: float, target: float, factor: float, delta: float) -> float:
    return lerpf(current, target, 1.0 - exp(-factor * delta * 60.0))

## Usage in a CharacterBody2D:
# velocity = MovementHelper.smooth_velocity(velocity, input * speed, 800.0, 600.0, delta)
# move_and_slide()
```

**3D first-person controller:**

```gdscript
extends CharacterBody3D

@export var speed: float = 5.0
@export var sprint_speed: float = 8.0
@export var jump_velocity: float = 4.5
@export var mouse_sensitivity: float = 0.002
@export var acceleration: float = 10.0
@export var friction: float = 8.0

@onready var camera_pivot: Node3D = $CameraPivot
@onready var camera: Camera3D = $CameraPivot/Camera3D

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")

func _ready() -> void:
    Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseMotion:
        var mouse_event: InputEventMouseMotion = event as InputEventMouseMotion
        rotate_y(-mouse_event.relative.x * mouse_sensitivity)
        camera_pivot.rotate_x(-mouse_event.relative.y * mouse_sensitivity)
        camera_pivot.rotation.x = clampf(camera_pivot.rotation.x, -PI / 2.0, PI / 2.0)

func _physics_process(delta: float) -> void:
    # Gravity
    if not is_on_floor():
        velocity.y -= gravity * delta

    # Jump
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity

    # Movement
    var current_speed: float = sprint_speed if Input.is_action_pressed("sprint") else speed
    var input_dir: Vector2 = Input.get_vector("move_left", "move_right", "move_forward", "move_back")
    var direction: Vector3 = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()

    if direction != Vector3.ZERO:
        velocity.x = lerpf(velocity.x, direction.x * current_speed, acceleration * delta)
        velocity.z = lerpf(velocity.z, direction.z * current_speed, acceleration * delta)
    else:
        velocity.x = lerpf(velocity.x, 0.0, friction * delta)
        velocity.z = lerpf(velocity.z, 0.0, friction * delta)

    move_and_slide()
```

---

## Physics Material

### PhysicsMaterial Resource

`PhysicsMaterial` controls how surfaces interact during collisions. Attach to `RigidBody2D/3D` or `StaticBody2D/3D`.

```gdscript
extends RigidBody2D

func _ready() -> void:
    var mat: PhysicsMaterial = PhysicsMaterial.new()
    mat.bounce = 0.7          # 0.0 = no bounce, 1.0 = perfect bounce
    mat.friction = 0.3        # 0.0 = ice, 1.0 = very sticky
    mat.rough = false         # if true, uses max friction instead of average
    mat.absorbent = false     # if true, uses min bounce instead of average
    physics_material_override = mat
```

**How combined values are computed:**

| Property | Default combination | With `rough` / `absorbent` |
|---|---|---|
| Friction | `sqrt(friction_a * friction_b)` (geometric mean) | `max(friction_a, friction_b)` if either is `rough` |
| Bounce | `max(bounce_a, bounce_b)` | `min(bounce_a, bounce_b)` if either is `absorbent` |

### Per-Body Overrides

```gdscript
# Ice floor (StaticBody2D)
extends StaticBody2D

func _ready() -> void:
    var ice: PhysicsMaterial = PhysicsMaterial.new()
    ice.friction = 0.02
    ice.bounce = 0.0
    physics_material_override = ice
```

```gdscript
# Bouncy ball (RigidBody2D)
extends RigidBody2D

func _ready() -> void:
    var rubber: PhysicsMaterial = PhysicsMaterial.new()
    rubber.friction = 0.8
    rubber.bounce = 0.9
    rubber.absorbent = false  # use max bounce (keeps bouncing high)
    physics_material_override = rubber
```

```gdscript
# Creating preset materials as resources (save as .tres files):
# res://physics_materials/ice.tres
# res://physics_materials/rubber.tres
# res://physics_materials/metal.tres

# Then load:
extends RigidBody2D

@export var material_preset: PhysicsMaterial

func _ready() -> void:
    if material_preset:
        physics_material_override = material_preset
```

---

## Quick Reference: Key Differences

| Body Type | Moved by | Collides | Use case |
|---|---|---|---|
| `StaticBody2D/3D` | Nothing (or constant velocity) | Yes | Walls, floors, platforms |
| `AnimatableBody2D/3D` | Code (moves and pushes others) | Yes | Moving platforms, elevators |
| `CharacterBody2D/3D` | `move_and_slide()` | Yes | Players, NPCs |
| `RigidBody2D/3D` | Physics engine | Yes | Crates, balls, ragdolls |
| `Area2D/3D` | Code (no physics) | No (detection only) | Triggers, pickups, zones |

## Quick Reference: Common Gotchas

1. **`move_and_slide()` uses `velocity` directly** -- do not multiply by `delta` for horizontal movement. Gravity should use `delta` because it accumulates.
2. **`get_overlapping_bodies()` returns empty in `_ready()`** -- the physics engine hasn't processed yet. Use `await get_tree().physics_frame` first.
3. **RigidBody2D contact signals require** `contact_monitor = true` AND `max_contacts_reported > 0`.
4. **Collision layer/mask are 1-indexed** in `set_collision_layer_value()` but 0-indexed in bitfield operations.
5. **`RayCast2D/3D` must be enabled** (`enabled = true`) to function.
6. **One-way collision is on the CollisionShape2D**, not on the body.
7. **`floor_snap_length`** prevents bouncing on slopes but can cause sticking. Set to `0` during jumps.
8. **Direct space state queries** (`intersect_ray`, etc.) can only be called during `_physics_process()` or after `await get_tree().physics_frame`.
