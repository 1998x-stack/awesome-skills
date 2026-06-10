---
name: manim
description: >
  Create mathematical animations using Manim (Mathematical Animation Engine).
  Use when Claude needs to create math visualizations, animate equations or
  formulas, plot function graphs, visualize geometric transformations, create
  3D mathematical surfaces, build step-by-step proof animations, or generate
  LaTeX-rendered formula animations.
---

# Manim Mathematical Animation Skill

Create precise, professional mathematical animations using Python code.

## Quick Start

```python
from manim import *

class Example(Scene):
    def construct(self):
        formula = MathTex(r"E = mc^2")
        self.play(Write(formula))
        self.wait()
```

Render: `manim -pql script.py Example`

## Core Workflow

1. **Create objects** → `Circle()`, `MathTex()`, `Axes()`
2. **Position them** → `.move_to()`, `.next_to()`, `.shift()`
3. **Animate** → `self.play(Create(obj))`, `Transform(a, b)`
4. **Wait** → `self.wait(seconds)`

## ⚠️ Critical Constraints (v0.19.2)

| Class | ✅ Allowed | ❌ Forbidden |
|-------|-----------|--------------|
| `Sector` | `radius`, `angle`, `start_angle` | `inner_radius`, `outer_radius` |
| `AnnularSector` | `inner_radius`, `outer_radius`, `angle` | - |
| `Rectangle` | `width`, `height` | `corner_radius` |
| `RoundedRectangle` | `corner_radius`, `width`, `height` | - |
| `MathTex` | ASCII, LaTeX only | Chinese/Unicode |
| `Arrow.scale()` | `scale_tips=True/False` | - |
| `SurroundingRectangle` | keyword args: `color=`, `buff=` | positional color/buff args |

### v0.19.0 Breaking Changes

```python
# SurroundingRectangle: positional args no longer work
# ❌ WRONG (old style)
SurroundingRectangle(some_mobject, RED, 0.3)

# ✅ CORRECT (new style)
SurroundingRectangle(some_mobject, color=RED, buff=0.3)
```

### Chinese + Math: Separation Required

```python
# ❌ WRONG: Chinese in MathTex
MathTex(r"\text{三角形}")  # Unicode Error!

# ✅ CORRECT: Separate Text and MathTex
chinese = Text("三角形", font="Noto Sans CJK SC")
math = MathTex(r"\triangle ABC")
VGroup(chinese, math).arrange(RIGHT)

# ✅ ALTERNATIVE: Use ctex template for Tex (not MathTex)
from manim import TexTemplateLibrary
tex = Tex(r"三角形 $\triangle ABC$", tex_template=TexTemplateLibrary.ctex)
```

### Degree Symbol

```python
# ❌ WRONG: Direct ° character
MathTex(r"90°")  # Error!

# ✅ CORRECT: Use LaTeX command
MathTex(r"90^\circ")
```

### LaTeX Fractions

```python
# ❌ WRONG: \over with double braces causes parsing error
MathTex(r"{{a} \over {b}}")  # Error!

# ✅ CORRECT: Use \frac
MathTex(r"\frac{a}{b}")
```

## Essential Classes

### Geometric Shapes

```python
Circle(radius=1, color=BLUE, fill_opacity=0.5)
Square(side_length=2)
Rectangle(width=4, height=2)
RoundedRectangle(corner_radius=0.5, width=4, height=2)  # For rounded corners
Line(start=LEFT, end=RIGHT)
Arrow(start=ORIGIN, end=UP)
Dot(point=ORIGIN, radius=0.1)
Polygon(ORIGIN, RIGHT, UP)  # Triangle
Sector(radius=1, angle=PI/3, start_angle=0)  # Pie slice (NO inner_radius!)
AnnularSector(inner_radius=1, outer_radius=2, angle=PI/2)  # Ring sector
```

### Text & Math

```python
Text("Hello", font_size=48)           # Plain text (supports Unicode)
Text("中文", font="Noto Sans CJK SC") # Chinese text with font
Tex(r"This is \LaTeX")                # LaTeX text mode
MathTex(r"\int_0^1 x^2 dx = \frac{1}{3}")  # Math mode (ASCII only!)
```

**LaTeX tips:**
- Use raw strings: `r"..."`
- MathTex auto-wraps in math mode
- Isolate parts with `{{ }}`: `MathTex(r"{{ a }}^2 + {{ b }}^2")`
- Use `\frac{}{}` instead of `\over`

### Coordinate Systems

```python
axes = Axes(
    x_range=[-3, 3, 1],   # [min, max, step]
    y_range=[-2, 2, 0.5],
    axis_config={"include_numbers": True}
)
graph = axes.plot(lambda x: np.sin(x), color=BLUE)
label = axes.get_graph_label(graph, r"\sin(x)")
```

### 3D Objects (use `ThreeDScene`)

```python
class My3D(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)
        axes = ThreeDAxes()
        sphere = Sphere(radius=1)
        self.add(axes, sphere)
```

## Essential Animations

| Animation | Effect |
|-----------|--------|
| `Create(obj)` | Draw outline |
| `Write(text)` | Handwriting effect |
| `FadeIn(obj)` / `FadeOut(obj)` | Fade |
| `Transform(a, b)` | Morph a into b |
| `ReplacementTransform(a, b)` | Replace a with b |
| `TransformMatchingTex(t1, t2)` | Smart TeX transform |
| `GrowFromCenter(obj)` | Grow from center |
| `Rotate(obj, angle=PI)` | Rotation |

### Animate Syntax (Recommended)

```python
self.play(obj.animate.shift(RIGHT * 2))
self.play(obj.animate.scale(0.5).set_color(RED))
self.play(obj.animate.rotate(PI/4).move_to(UP))
```

### Animation Parameters

```python
self.play(Create(circle), run_time=2, rate_func=smooth)
# rate_func options: smooth, linear, rush_into, rush_from, there_and_back
```

## Positioning

```python
# Absolute
obj.move_to(ORIGIN)
obj.move_to([1, 2, 0])

# Relative
obj.shift(RIGHT * 2 + UP)
obj.next_to(other, DOWN, buff=0.5)
obj.to_edge(LEFT)
obj.to_corner(UR)

# Alignment
obj.align_to(other, UP)  # Align top edges
```

**Direction constants:** `UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR, ORIGIN, OUT, IN`

## Grouping

```python
group = VGroup(circle, square, triangle)
group.arrange(RIGHT, buff=0.5)       # Horizontal layout
group.arrange(DOWN, aligned_edge=LEFT)  # Vertical, left-aligned
group.set_color(BLUE)                # Apply to all
group[0].set_color(RED)              # Access by index
```

## ValueTracker & Updaters

For dynamic animations:

```python
t = ValueTracker(0)

# Method 1: always_redraw
dot = always_redraw(lambda: Dot([t.get_value(), 0, 0]))

# Method 2: add_updater
label = DecimalNumber(0)
label.add_updater(lambda m: m.set_value(t.get_value()))

self.add(dot, label)
self.play(t.animate.set_value(5), run_time=3)
```

## CLI Quick Reference

```bash
# Quality presets
-ql   # 480p 15fps (preview)
-qm   # 720p 30fps
-qh   # 1080p 60fps
-qk   # 4K 60fps

# Common flags
-p    # Preview after render
-s    # Save last frame only
-t    # Transparent background
-c WHITE  # Background color
--format gif  # Output GIF

# Examples
manim -pql scene.py MyScene     # Quick preview
manim -qh scene.py MyScene      # High quality
manim -pql --format gif scene.py MyScene  # GIF output
```

## Common Patterns

### Equation Derivation

```python
step1 = MathTex(r"(a+b)^2")
step2 = MathTex(r"a^2 + 2ab + b^2")
self.play(Write(step1))
self.wait()
self.play(TransformMatchingTex(step1, step2))
```

### Function Animation

```python
axes = Axes(x_range=[-3, 3], y_range=[-2, 2])
t = ValueTracker(-3)

graph = always_redraw(
    lambda: axes.plot(lambda x: np.sin(x), x_range=[-3, t.get_value()], color=BLUE)
)
dot = always_redraw(
    lambda: Dot(axes.c2p(t.get_value(), np.sin(t.get_value())))
)

self.add(axes, graph, dot)
self.play(t.animate.set_value(3), run_time=4)
```

### Sub-formula Coloring

```python
eq = MathTex(r"{{ a }}^2 + {{ b }}^2 = {{ c }}^2")
eq.set_color_by_tex("a", RED)
eq.set_color_by_tex("b", BLUE)
eq.set_color_by_tex("c", GREEN)
```

### Moving Camera (3D)

```python
class CameraMove(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=60*DEGREES, theta=-45*DEGREES)
        # ...
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(3)
        self.stop_ambient_camera_rotation()
```

## Color Constants

`RED, BLUE, GREEN, YELLOW, ORANGE, PURPLE, PINK, TEAL, GOLD, MAROON, WHITE, BLACK, GRAY`

Variants: `BLUE_A, BLUE_B, BLUE_C, BLUE_D, BLUE_E` (light to dark)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| LaTeX error | Check LaTeX installation; use raw strings `r"..."` |
| Chinese in MathTex | Use `Text("中文", font="Noto Sans CJK SC")` instead |
| Degree symbol error | Use `^\circ` not `°` |
| `corner_radius` error | Use `RoundedRectangle` not `Rectangle` |
| `inner_radius` error on Sector | Use `AnnularSector` for ring sectors |
| Double brace LaTeX error | Use `\frac{a}{b}` not `{{a}\over{b}}` |
| SurroundingRectangle positional args | Use keyword: `SurroundingRectangle(obj, color=RED, buff=0.3)` |
| Slow rendering | Use `-ql` for preview |
| Memory error | Use `self.remove(obj)` to free objects |
| Angle arc on wrong side | Check `other_angle` parameter; use cross product to determine direction |
| Point position incorrect | Never guess coordinates; calculate mathematically |
| Elements off-screen | Check bounds: x∈[-7,7], y∈[-4,4] |

## Angle & Geometry Precision

### Angle Class Parameters

```python
Angle(line1, line2,
      radius=0.5,           # Arc radius
      quadrant=(1, 1),      # Anchor point: (1=end, -1=start) for each line
      other_angle=False,    # True for the complementary angle
      elbow=False)          # True for right angle symbol
```

### quadrant Combinations

| quadrant | line1 anchor | line2 anchor |
|----------|--------------|--------------|
| (1, 1)   | end point    | end point    |
| (-1, 1)  | start point  | end point    |
| (1, -1)  | end point    | start point  |
| (-1, -1) | start point  | start point  |

### Correct Angle Usage

```python
# Create angle at vertex B (angle ABC)
line_BA = Line(B, A)  # From B to A
line_BC = Line(B, C)  # From B to C
angle = Angle(line_BA, line_BC, radius=0.5)

# For right angle symbol
right_angle = RightAngle(line1, line2, length=0.3)
# OR
angle = Angle(line1, line2, radius=0.3, elbow=True)

# Using three points (RECOMMENDED)
angle = Angle.from_three_points(A, B, C, radius=0.5)  # Angle at B
```

### Arc Direction Control

```python
# Positive angle = counterclockwise
Arc(radius=1, start_angle=0, angle=PI/2)      # CCW 90°

# Negative angle = clockwise  
Arc(radius=1, start_angle=PI/2, angle=-PI/2)  # CW 90°

# ArcBetweenPoints: radius sign controls direction
ArcBetweenPoints(start, end, radius=1)   # CCW (arc on left side)
ArcBetweenPoints(start, end, radius=-1)  # CW (arc on right side)
```

### Geometry Precision Rules

1. **NEVER guess coordinates** - Calculate all points mathematically
2. **Store geometry in setup** - Initialize once, reference everywhere
3. **Verify relationships** - Check perpendicular/parallel/collinear programmatically
4. **Use numpy** - All geometric calculations through `np.linalg`

```python
# ❌ WRONG: Guessing coordinates
midpoint = np.array([1.5, 2.3, 0])  # Arbitrary values

# ✅ CORRECT: Calculate precisely
midpoint = (point_A + point_B) / 2

# Perpendicular foot (point to line)
def foot_of_perpendicular(point, line_start, line_end):
    line_vec = line_end - line_start
    t = np.dot(point - line_start, line_vec) / np.dot(line_vec, line_vec)
    return line_start + t * line_vec
```

## References

For advanced topics, see:
- `references/advanced-patterns.md` - Complex animation patterns
- `references/3d-guide.md` - 3D scene techniques
- `references/latex-cheatsheet.md` - LaTeX math symbols
- `references/geometry-constraints.md` - Precise geometry calculations
