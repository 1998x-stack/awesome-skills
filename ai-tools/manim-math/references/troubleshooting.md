# Troubleshooting Guide

Common errors and solutions for Manim math animations.

## Quick Diagnosis

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| LaTeX Unicode error | Chinese in MathTex | Use Text() for Chinese |
| Angle on wrong side | Wrong quadrant/other_angle | Try different values |
| Lines not perpendicular | Guessed coordinates | Calculate with formula |
| Element outside frame | Missing bounds check | Add clipping/scaling |
| Slow rendering | High quality + long waits | Use -ql for preview |

## LaTeX Errors

### Error: "Unicode character U+... not set up for use with LaTeX"

**Cause:** Chinese characters in MathTex

```python
# ❌ WRONG
angle_text = MathTex(r"角度 = 90^\circ")

# ✅ CORRECT
chinese = Text("角度 =", font="Noto Sans CJK SC", font_size=24)
math = MathTex(r"90^\circ", font_size=24)
VGroup(chinese, math).arrange(RIGHT, buff=0.1)
```

### Error: "Missing { inserted" or "Extra }"

**Cause:** Unbalanced braces or double braces

```python
# ❌ WRONG
formula = MathTex(r"{{a}\over{b}}")

# ✅ CORRECT
formula = MathTex(r"\frac{a}{b}")

# ✅ CORRECT - For part isolation
formula = MathTex(r"{{ a }} + {{ b }}")  # Space-separated
```

### Error: "Undefined control sequence \°"

**Cause:** Direct degree symbol

```python
# ❌ WRONG
MathTex(r"90°")

# ✅ CORRECT
MathTex(r"90^\circ")
```

## Geometry Errors

### Problem: Angle arc on wrong side

**Diagnosis:** Run this check:

```python
# Add temporary debugging
v1 = point1 - vertex
v2 = point2 - vertex
cross_z = v1[0] * v2[1] - v1[1] * v2[0]
print(f"Cross product z: {cross_z}")
print(f"If > 0: counterclockwise, if < 0: clockwise")
```

**Solution 1:** Try different quadrant values

```python
# Try each systematically
for q in [(1,1), (-1,1), (1,-1), (-1,-1)]:
    angle = Angle(line1, line2, quadrant=q)
    # Test which looks correct
```

**Solution 2:** Use other_angle parameter

```python
if cross_z < 0:
    angle = Angle(line1, line2, other_angle=True)
else:
    angle = Angle(line1, line2, other_angle=False)
```

**Solution 3:** Swap line order

```python
# Sometimes easier than fixing parameters
angle = Angle(line2, line1)  # Reverses direction
```

### Problem: Lines not perpendicular/parallel

**Diagnosis:**

```python
# Check dot product (should be ~0 for perpendicular)
dot = np.dot(vec1[:2], vec2[:2])
print(f"Dot product: {dot} (should be < 1e-6)")

# Check cross product (should be ~0 for parallel)
cross = np.cross(vec1[:2], vec2[:2])
print(f"Cross product: {cross} (should be < 1e-6)")
```

**Solution:** Never guess coordinates

```python
# ❌ WRONG
foot = np.array([1.5, 2.3, 0])  # Guessed!

# ✅ CORRECT
line_vec = line_end - line_start
point_vec = point - line_start
t = np.dot(point_vec, line_vec) / np.dot(line_vec, line_vec)
foot = line_start + t * line_vec

# Verify
perp_vec = foot - point
assert abs(np.dot(perp_vec[:2], line_vec[:2])) < 1e-6
```

### Problem: Distances not equal

**Diagnosis:**

```python
d1 = np.linalg.norm(point - A)
d2 = np.linalg.norm(point - B)
d3 = np.linalg.norm(point - C)
print(f"Distances: {d1:.6f}, {d2:.6f}, {d3:.6f}")
print(f"Max difference: {max(d1,d2,d3) - min(d1,d2,d3)}")
```

**Solution:** Verify calculation formula

```python
# For circumcenter, recalculate from scratch
def verify_circumcenter(A, B, C, O):
    epsilon = 1e-6
    r_A = np.linalg.norm(O - A)
    r_B = np.linalg.norm(O - B)
    r_C = np.linalg.norm(O - C)
    
    if abs(r_A - r_B) > epsilon:
        print(f"ERROR: r_A={r_A:.6f}, r_B={r_B:.6f}")
        print(f"Difference: {abs(r_A - r_B):.9f}")
        return False
    
    if abs(r_B - r_C) > epsilon:
        print(f"ERROR: r_B={r_B:.6f}, r_C={r_C:.6f}")
        print(f"Difference: {abs(r_B - r_C):.9f}")
        return False
    
    return True
```

## Rendering Issues

### Problem: Element outside visible area

**Diagnosis:**

```python
def check_bounds(mobject):
    bbox = mobject.get_bounding_box()
    print(f"X range: [{bbox[0][0]:.2f}, {bbox[1][0]:.2f}]")
    print(f"Y range: [{bbox[0][1]:.2f}, {bbox[1][1]:.2f}]")
    print(f"Within bounds: x∈[-4.5,4.5], y∈[-8,8]")
```

**Solution:** Scale or reposition

```python
# Method 1: Scale entire scene
SCALE = 0.8
all_elements = VGroup(triangle, labels, lines)
all_elements.scale(SCALE)

# Method 2: Reposition
all_elements.move_to(UP * 1)  # Shift up

# Method 3: Clip to safe zone
def clip_to_safe_zone(mobject):
    bbox = mobject.get_bounding_box()
    if bbox[1][0] > 4.0:  # Too far right
        mobject.shift(LEFT * (bbox[1][0] - 4.0))
    if bbox[0][1] < -7.0:  # Too far down
        mobject.shift(UP * (-7.0 - bbox[0][1]))
    return mobject
```

### Problem: Text overlapping

**Solution:** Smart placement with fallback

```python
def place_label_smart(mobject, label, preferred_dir=UR, buff=0.2):
    """Try multiple positions until one works"""
    directions = [preferred_dir, UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR]
    
    for direction in directions:
        label.next_to(mobject, direction, buff=buff)
        
        # Check if in bounds
        bbox = label.get_bounding_box()
        if (-4 < bbox[0][0] < 4 and -7 < bbox[0][1] < 7):
            # Check if overlaps with existing elements
            if not overlaps_with_existing(label):
                return label
    
    # Fallback: shrink and use preferred direction
    label.scale(0.7)
    label.next_to(mobject, preferred_dir, buff=buff)
    return label
```

### Problem: Slow rendering

**Quick fixes:**

```bash
# 1. Use lower quality for testing
manim -ql script.py Scene  # Low quality, fast

# 2. Reduce wait times temporarily
# Replace: self.wait(2.0)
# With: self.wait(0.2)

# 3. Test specific scene only
manim -ql script.py Scene --scene_names SpecificScene

# 4. Skip to time point
manim -ql script.py Scene -s  # Save last frame only
```

**Code optimization:**

```python
# ❌ SLOW - Redraws every frame
dot = always_redraw(lambda: Dot(complex_calculation()))

# ✅ FAST - Update only when needed
dot = Dot(initial_position)
self.add(dot)
# Later, when value changes:
self.play(dot.animate.move_to(new_position))
```

## Animation Issues

### Problem: Jerky or unnatural motion

**Diagnosis:** Check run_time and rate_func

```python
# Too fast
self.play(Create(complex_shape), run_time=0.2)  # Bad!

# Too slow
self.play(Write(short_text), run_time=3.0)  # Boring!
```

**Solution:** Use appropriate timing

```python
# Recommended timings
TIMINGS = {
    'simple_shape': 0.5-1.0,
    'complex_shape': 1.0-1.5,
    'short_text': 0.4-0.8,
    'formula': 0.6-1.0,
    'transform': 0.8-1.2,
    'key_pause': 2.0-3.0
}

# Use rate functions for natural motion
self.play(
    obj.animate.move_to(target),
    rate_func=smooth,  # smooth, linear, rush_into, rush_from
    run_time=1.0
)
```

### Problem: Elements appear in wrong order

**Solution:** Track creation order carefully

```python
# Method 1: Explicit ordering with lag_ratio
elements = VGroup(elem1, elem2, elem3)
self.play(
    *[FadeIn(e) for e in elements],
    lag_ratio=0.3  # 30% overlap
)

# Method 2: Sequential with proper cleanup
self.play(Create(line1))
self.wait(0.5)
self.play(Create(line2))
self.play(FadeOut(line1))  # Remove when done
```

## Common Patterns

### Debug Checklist Script

```python
def debug_geometry(self):
    """Run this before rendering to catch errors"""
    checks = []
    
    # 1. Check all points defined
    required_points = ['A', 'B', 'C', 'O', 'I', 'G']
    for pt in required_points:
        if not hasattr(self, pt):
            checks.append(f"Missing point: {pt}")
    
    # 2. Check circumcenter
    if hasattr(self, 'O'):
        r_A = np.linalg.norm(self.O - self.A)
        r_B = np.linalg.norm(self.O - self.B)
        r_C = np.linalg.norm(self.O - self.C)
        if abs(r_A - r_B) > 1e-6 or abs(r_B - r_C) > 1e-6:
            checks.append(f"Circumcenter error: {r_A:.6f}, {r_B:.6f}, {r_C:.6f}")
    
    # 3. Check bounds
    for name in ['A', 'B', 'C']:
        pt = getattr(self, name)
        if abs(pt[0]) > 4.5 or abs(pt[1]) > 8:
            checks.append(f"Point {name} out of bounds: {pt}")
    
    # 4. Report
    if checks:
        print("❌ ERRORS FOUND:")
        for c in checks:
            print(f"  - {c}")
        raise ValueError("Geometry check failed")
    else:
        print("✓ All checks passed")
```

### Quick Test Template

```python
class QuickTest(Scene):
    """Use this to test specific elements"""
    def construct(self):
        # Test single element
        element_to_test = self.create_problem_element()
        self.add(element_to_test)
        
        # Add reference grid for positioning
        grid = self.create_reference_grid()
        self.add(grid)
        
        self.wait()
    
    def create_reference_grid(self):
        """Helper grid for positioning"""
        lines = VGroup()
        for x in range(-4, 5):
            lines.add(Line([x, -8, 0], [x, 8, 0], 
                          stroke_width=0.5, color=GRAY))
        for y in range(-8, 9):
            lines.add(Line([-4.5, y, 0], [4.5, y, 0],
                          stroke_width=0.5, color=GRAY))
        return lines
```

## Getting Help

If problem persists:

1. **Check example scripts** in `scripts/` folder
2. **Review constraints** in `references/manim-constraints.md`
3. **Verify calculations** in `references/geometry-calculations.md`
4. **Simplify**: Remove elements until error disappears
5. **Test in isolation**: Create QuickTest scene for problem element
