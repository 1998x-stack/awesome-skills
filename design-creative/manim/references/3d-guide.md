# Manim 3D Scene Guide

## Basics

Use `ThreeDScene` instead of `Scene`:

```python
from manim import *

class My3DScene(ThreeDScene):
    def construct(self):
        # Set camera
        self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)
        
        # Create 3D axes
        axes = ThreeDAxes()
        self.add(axes)
```

## Coordinate System

```
        Z (OUT)
        │
        │
        └───── Y (UP in 2D, but right in 3D view)
       /
      /
     X (RIGHT)
```

**Direction constants for 3D:**
- `OUT` = (0, 0, 1) - toward viewer
- `IN` = (0, 0, -1) - away from viewer

## Camera Control

### Initial Orientation

```python
self.set_camera_orientation(
    phi=75 * DEGREES,     # Angle from Z-axis (vertical tilt)
    theta=-45 * DEGREES,  # Rotation around Z-axis (horizontal)
    gamma=0,              # Roll
    zoom=1,
    frame_center=ORIGIN
)
```

### Camera Animation

```python
# Move camera smoothly
self.move_camera(
    phi=60 * DEGREES,
    theta=30 * DEGREES,
    run_time=2
)

# Ambient rotation (continuous)
self.begin_ambient_camera_rotation(rate=0.2)  # radians/sec
self.wait(5)
self.stop_ambient_camera_rotation()

# Zoom
self.move_camera(zoom=2, run_time=1)
```

## 3D Primitives

```python
# Sphere
sphere = Sphere(
    radius=1,
    resolution=(20, 20),  # (u_segments, v_segments)
    fill_opacity=0.7
)

# Cube
cube = Cube(
    side_length=2,
    fill_color=BLUE,
    fill_opacity=0.5
)

# Cylinder
cylinder = Cylinder(
    radius=0.5,
    height=2,
    direction=UP,  # Axis direction
    fill_opacity=0.8
)

# Cone
cone = Cone(
    base_radius=1,
    height=2,
    direction=UP,
    fill_opacity=0.7
)

# Torus
torus = Torus(
    major_radius=2,
    minor_radius=0.5
)

# Line3D
line = Line3D(
    start=ORIGIN,
    end=[1, 1, 1],
    color=RED
)

# Arrow3D
arrow = Arrow3D(
    start=ORIGIN,
    end=[1, 2, 1],
    color=YELLOW
)
```

## 3D Axes

```python
axes = ThreeDAxes(
    x_range=[-5, 5, 1],
    y_range=[-5, 5, 1],
    z_range=[-3, 3, 1],
    x_length=10,
    y_length=10,
    z_length=6,
    axis_config={"include_tip": True}
)

# Add labels
labels = axes.get_axis_labels(
    x_label="x",
    y_label="y",
    z_label="z"
)
```

## Parametric Surfaces

```python
class SurfaceExample(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)
        
        axes = ThreeDAxes()
        
        # Parametric surface: z = sin(x) * cos(y)
        surface = Surface(
            lambda u, v: axes.c2p(u, v, np.sin(u) * np.cos(v)),
            u_range=[-PI, PI],
            v_range=[-PI, PI],
            resolution=(30, 30),
            fill_opacity=0.7
        )
        
        # Checkerboard coloring
        surface.set_fill_by_checkerboard(BLUE, GREEN, opacity=0.5)
        
        self.add(axes, surface)
        self.begin_ambient_camera_rotation()
        self.wait(5)
```

### Common Surfaces

```python
# Gaussian surface
def gaussian(u, v):
    x, y = u, v
    z = np.exp(-(x**2 + y**2))
    return np.array([x, y, z])

# Saddle surface
def saddle(u, v):
    return np.array([u, v, u**2 - v**2])

# Torus parametric
def torus_param(u, v, R=2, r=0.5):
    return np.array([
        (R + r*np.cos(v)) * np.cos(u),
        (R + r*np.cos(v)) * np.sin(u),
        r * np.sin(v)
    ])

# Sphere parametric
def sphere_param(u, v, r=1):
    return np.array([
        r * np.sin(u) * np.cos(v),
        r * np.sin(u) * np.sin(v),
        r * np.cos(u)
    ])
```

## Parametric Curves in 3D

```python
class Helix(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)
        
        axes = ThreeDAxes()
        
        helix = ParametricFunction(
            lambda t: np.array([
                np.cos(t),
                np.sin(t),
                t / 4
            ]),
            t_range=[0, 4*PI],
            color=RED
        )
        
        self.add(axes, helix)
```

## 2D Objects in 3D Space

```python
class Text3DExample(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)
        
        axes = ThreeDAxes()
        
        # 2D text fixed to frame (doesn't rotate with camera)
        title = Text("3D Demo").to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        
        # 2D object in 3D space (rotates with scene)
        circle = Circle(color=RED)
        circle.rotate(PI/2, axis=RIGHT)  # Rotate to XZ plane
        
        self.add(axes, circle)
```

## Transformations in 3D

```python
# Rotation around axes
obj.rotate(PI/4, axis=RIGHT)  # Around X
obj.rotate(PI/4, axis=UP)     # Around Y
obj.rotate(PI/4, axis=OUT)    # Around Z

# Rotation around arbitrary axis
obj.rotate(PI/4, axis=[1, 1, 0])

# Shift in 3D
obj.shift(OUT * 2)
obj.shift([1, 2, 3])

# Scale (uniform or per-axis)
obj.scale(2)
obj.scale([1, 2, 0.5])  # Different scale per axis
```

## Lighting (OpenGL Renderer)

For ManimCE with OpenGL:

```python
# Note: Lighting is more customizable with ManimGL
# In ManimCE, surfaces automatically have basic shading

surface.set_style(
    fill_opacity=0.7,
    stroke_width=0.5,
    stroke_color=WHITE
)
```

## Example: Animated 3D Surface

```python
class AnimatedSurface(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)
        
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-2, 2])
        
        t = ValueTracker(0)
        
        surface = always_redraw(lambda: Surface(
            lambda u, v: axes.c2p(
                u, v,
                np.sin(u + t.get_value()) * np.cos(v + t.get_value())
            ),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(20, 20),
            fill_opacity=0.7,
            fill_color=BLUE
        ))
        
        self.add(axes, surface)
        self.begin_ambient_camera_rotation(rate=0.1)
        self.play(t.animate.set_value(2*PI), run_time=6, rate_func=linear)
```

## Example: Vector Field in 3D

```python
class VectorField3D(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)
        
        axes = ThreeDAxes()
        
        def vector_func(pos):
            x, y, z = pos
            return np.array([-y, x, 0])  # Rotation field
        
        vectors = VGroup()
        for x in np.arange(-2, 2.5, 1):
            for y in np.arange(-2, 2.5, 1):
                for z in np.arange(-1, 1.5, 1):
                    pos = np.array([x, y, z])
                    vec = vector_func(pos)
                    if np.linalg.norm(vec) > 0.1:
                        arrow = Arrow3D(
                            start=pos,
                            end=pos + vec * 0.3,
                            color=BLUE
                        )
                        vectors.add(arrow)
        
        self.add(axes, vectors)
        self.begin_ambient_camera_rotation()
        self.wait(5)
```

## Performance Notes

1. **Lower resolution** - Use smaller resolution values for surfaces during development
2. **Fewer segments** - Reduce sphere/cylinder resolution
3. **OpenGL renderer** - Consider ManimGL for complex 3D scenes
4. **Quality flag** - Always use `-ql` for 3D preview (rendering is slow)

## Common Issues

| Issue | Solution |
|-------|----------|
| 2D text invisible | Use `add_fixed_in_frame_mobjects()` |
| Surface inside-out | Try negative normal or reverse u/v range |
| Z-fighting | Slightly offset overlapping surfaces |
| Slow rendering | Reduce resolution, use `-ql` |
