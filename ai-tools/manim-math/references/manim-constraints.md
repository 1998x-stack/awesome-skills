# Manim 0.19.2 Constraints and Known Issues

Complete reference for version-specific limitations and workarounds.

## Critical Constraints

### Text and LaTeX

#### Chinese Characters

**Problem:** MathTex cannot render Chinese characters (Unicode error)

```python
# ❌ WRONG - Causes LaTeX Unicode error
title = MathTex(r"三角形面积")
formula = MathTex(r"\text{勾股定理}")

# ✅ CORRECT - Separate Chinese and math
chinese = Text("三角形面积", font="Noto Sans CJK SC", font_size=36)
math = MathTex(r"S = \frac{1}{2}bh", font_size=28)
VGroup(chinese, math).arrange(DOWN)

# ✅ ALTERNATIVE - Use ctex template (less reliable)
from manim import TexTemplateLibrary
tex = Tex(r"三角形 $A=\frac{1}{2}bh$", tex_template=TexTemplateLibrary.ctex)
```

**Font recommendations:**
- Simplified Chinese: `"Noto Sans CJK SC"`, `"SimHei"`, `"Microsoft YaHei"`
- Traditional Chinese: `"Noto Sans CJK TC"`

#### Degree Symbol

**Problem:** Direct `°` symbol not supported

```python
# ❌ WRONG
angle_label = MathTex(r"90°")

# ✅ CORRECT
angle_label = MathTex(r"90^\circ")
# OR
angle_label = MathTex(r"90^{\circ}")
```

#### LaTeX Braces

**Problem:** Double braces cause parsing errors

```python
# ❌ WRONG - Parser error
formula = MathTex(r"{{a} \over {b}}")
formula = MathTex(r"{{\frac{a}{b}}}")

# ✅ CORRECT - Use proper LaTeX commands
formula = MathTex(r"\frac{a}{b}")

# ✅ CORRECT - Single braces for isolation
formula = MathTex(r"{{ a }} + {{ b }}")  # Each part isolated
```

### Shape Classes

#### Sector vs AnnularSector

```python
# ❌ WRONG - inner_radius removed in 0.19
sector = Sector(radius=2, inner_radius=0.5, outer_radius=2)

# ✅ CORRECT - Use AnnularSector for ring sectors
sector = AnnularSector(inner_radius=0.5, outer_radius=2, angle=PI/2)

# ✅ CORRECT - Use Sector for simple sectors
sector = Sector(radius=2, angle=PI/2, start_angle=0)
```

#### Rectangle Corner Radius

```python
# ❌ WRONG - corner_radius not supported
rect = Rectangle(width=4, height=2, corner_radius=0.2)

# ✅ CORRECT - Use RoundedRectangle
rect = RoundedRectangle(width=4, height=2, corner_radius=0.2)
```

### Arrow Scaling

```python
# ❌ WRONG - scale_tips parameter removed
arrow = Arrow(start=ORIGIN, end=RIGHT*2)
arrow.scale(0.5, scale_tips=False)

# ✅ CORRECT - Tips scale automatically now
arrow = Arrow(start=ORIGIN, end=RIGHT*2)
arrow.scale(0.5)  # Tips maintain proportions

# ✅ WORKAROUND - Recreate arrow if tip size critical
new_end = arrow.get_start() + 0.5 * (arrow.get_end() - arrow.get_start())
new_arrow = Arrow(start=arrow.get_start(), end=new_end, 
                  buff=0, tip_length=0.2)  # Specify tip size
```

## Angle Creation Issues

### Quadrant Confusion

**Problem:** Angle arc appears on wrong side

**Root cause:** Misunderstanding `quadrant` parameter

```python
# quadrant=(a, b) where:
# a: -1 (line1 start side) or 1 (line1 end side)
# b: -1 (line2 start side) or 1 (line2 end side)

# Example: Angle at vertex B
line_BA = Line(B, A)
line_BC = Line(B, C)

# Try different quadrants to get correct arc position
angle = Angle(line_BA, line_BC, quadrant=(1, 1))  # Default
# If wrong side, try: (-1, 1), (1, -1), or (-1, -1)
```

**Solution:** Use `Angle.from_three_points` (clearer):

```python
angle = Angle.from_three_points(A, B, C, radius=0.5)
```

### other_angle Parameter

**Problem:** Angle arc on wrong side even with correct quadrant

```python
# Calculate cross product to determine direction
v1 = point1 - vertex
v2 = point2 - vertex
cross_z = v1[0] * v2[1] - v1[1] * v2[0]

if cross_z > 0:
    # Counterclockwise from v1 to v2
    angle = Angle(line1, line2, other_angle=False)
else:
    # Clockwise from v1 to v2
    angle = Angle(line1, line2, other_angle=True)
```

### Right Angle Marks

```python
# Method 1: RightAngle class (recommended)
right_angle = RightAngle(line1, line2, length=0.3, quadrant=(1,1))

# Method 2: Angle with elbow
angle = Angle(line1, line2, radius=0.3, elbow=True, quadrant=(1,1))

# Method 3: Manual square (full control)
def create_right_angle_mark(corner, p1, p2, size=0.2):
    v1 = (p1 - corner) / np.linalg.norm(p1 - corner) * size
    v2 = (p2 - corner) / np.linalg.norm(p2 - corner) * size
    return Polygon(corner, corner+v1, corner+v1+v2, corner+v2, 
                   color=YELLOW, fill_opacity=0)
```

## Common Errors and Fixes

### LaTeX Compilation Errors

**Error:** `LaTeX Error: Unicode character...`

```python
# ❌ Cause: Chinese in MathTex
MathTex(r"角度 = 90^\circ")

# ✅ Fix: Separate text
VGroup(Text("角度 =", font="Noto Sans CJK SC"), 
       MathTex(r"90^\circ")).arrange(RIGHT)
```

**Error:** `Missing { inserted` or `Extra } or forgotten {`

```python
# ❌ Cause: Unbalanced braces
MathTex(r"{{a}\over{b}}")

# ✅ Fix: Use \frac
MathTex(r"\frac{a}{b}")
```

### Geometry Errors

**Error:** "Angle arc on wrong side"

```python
# ✅ Fix 1: Try different quadrant values
angle = Angle(line1, line2, quadrant=(-1, 1))

# ✅ Fix 2: Use other_angle
angle = Angle(line1, line2, other_angle=True)

# ✅ Fix 3: Swap line order
angle = Angle(line2, line1)  # Reverses direction
```

**Error:** "Perpendicular lines not perpendicular"

```python
# ❌ Cause: Guessed coordinates
foot = np.array([1.5, 2.0, 0])  # Wrong!

# ✅ Fix: Calculate foot
foot = GeometryCalculator.perpendicular_foot(point, line_start, line_end)
```

### Rendering Issues

**Error:** Elements outside frame

```python
# ✅ Check bounds before adding
def is_within_bounds(mobject):
    bbox = mobject.get_bounding_box()
    return (bbox[0][0] > -4.5 and bbox[1][0] < 4.5 and
            bbox[0][1] > -8 and bbox[1][1] < 8)

if is_within_bounds(obj):
    self.add(obj)
else:
    obj.scale(0.8).move_to(ORIGIN)  # Adjust
```

**Error:** Text overlapping

```python
# ✅ Smart label placement
def place_label_safe(mobject, label, direction=UR):
    for dir in [direction, UP, DOWN, LEFT, RIGHT]:
        label.next_to(mobject, dir, buff=0.2)
        if is_within_bounds(label):
            return label
    return label.scale(0.7)  # Shrink if no space
```

## Performance Issues

### Slow Rendering

**Problem:** Long render times

```python
# ✅ Use lower quality for preview
manim -ql script.py Scene  # Fast preview

# ✅ Limit wait times during testing
self.wait(0.1)  # Instead of self.wait(2)

# ✅ Comment out expensive animations
# self.play(Create(complex_shape), run_time=3)
```

### Memory Issues

**Problem:** Out of memory with many objects

```python
# ✅ Remove objects when done
self.play(FadeOut(temp_group))
self.remove(temp_group)  # Free memory

# ✅ Use always_redraw sparingly
# Create once instead of redrawing every frame
dot = Dot(point)
self.add(dot)
# Instead of:
# dot = always_redraw(lambda: Dot(tracker.get_value()))
```

## Version-Specific Workarounds

### No Native Grid Support

```python
# Manual grid creation
def create_grid(x_range, y_range, step=1):
    lines = VGroup()
    for x in np.arange(x_range[0], x_range[1]+step, step):
        lines.add(Line([x, y_range[0], 0], [x, y_range[1], 0], 
                      stroke_width=1, color=GRAY_B))
    for y in np.arange(y_range[0], y_range[1]+step, step):
        lines.add(Line([x_range[0], y, 0], [x_range[1], y, 0],
                      stroke_width=1, color=GRAY_B))
    return lines
```

### Limited 3D Camera Control

```python
class My3DScene(ThreeDScene):
    def construct(self):
        # Set initial view
        self.set_camera_orientation(phi=60*DEGREES, theta=-45*DEGREES)
        
        # Animate camera
        self.move_camera(phi=70*DEGREES, theta=-30*DEGREES, run_time=2)
        
        # Ambient rotation
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(5)
        self.stop_ambient_camera_rotation()
```

## Testing Checklist

Before final render, verify:

- [ ] No Chinese in MathTex
- [ ] All degree symbols use `^\circ`
- [ ] All coordinates calculated, not guessed
- [ ] Geometry verification passes
- [ ] Angles appear on correct side
- [ ] All elements within frame bounds
- [ ] No text overlapping
- [ ] Reasonable render time
- [ ] Clean up temporary objects
