---
name: manim-math
description: >
  Professional mathematical teaching animation creation for K-12 students using Manim 0.19.2.
  Use when creating educational math videos with precise geometry, animated proofs, step-by-step
  explanations, or visual demonstrations of mathematical concepts. Supports TikTok vertical format
  (1080×1920), includes geometry calculation libraries, verification systems, and proven animation
  patterns. Triggers on requests to: create math animations, build teaching videos, visualize
  geometry problems, animate equations, or produce educational content for social media platforms.
---

# Manim Math - Professional Mathematical Teaching Animations

Create high-quality educational math animations for K-12 students using Manim 0.19.2.

## Quick Start

```python
from manim import *
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16

class MathLesson(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a2e"
        self.setup_geometry()
        # Your animation code here
```

## Core Workflow

1. **Read references** - Check `references/geometry-calculations.md` and `references/manim-constraints.md`
2. **Create storyboard** - Plan scenes with `references/storyboard-template.md`
3. **Write code** - Implement with precise geometry calculations
4. **Verify** - Run verification script before rendering

## Critical Rules

### Manim 0.19.2 Constraints

**FORBIDDEN:**
- Chinese in `MathTex()` → Use `Text()` instead
- Degree symbol `°` → Use `r"^\circ"`
- `Sector(inner_radius=...)` → Use `AnnularSector()` instead
- `Rectangle(corner_radius=...)` → Use `RoundedRectangle()` instead
- Double braces `{{...}}` in formulas → Use `\frac{a}{b}` not `{{a}\over{b}}`
- `Arrow.scale(scale_tips=...)` → Not supported in 0.19.2

**REQUIRED:**
- All coordinates via NumPy calculation, never guessing
- Geometry verification after setup
- Chinese text: `Text("中文", font="Noto Sans CJK SC")`
- Math formulas: `MathTex(r"E=mc^2")`

### Example: Correct Text Handling

```python
# ❌ WRONG - Causes LaTeX error
title = MathTex(r"三角形面积")

# ✅ CORRECT - Separate Chinese and math
chinese = Text("三角形面积", font="Noto Sans CJK SC", font_size=36)
formula = MathTex(r"S = \frac{1}{2}bh", font_size=28)
VGroup(chinese, formula).arrange(DOWN)
```

## Geometry Architecture

### Unified Initialization Pattern

```python
class GeometryScene(Scene):
    def construct(self):
        # Phase 1: Calculate ALL geometry once
        self.setup_geometry()
        
        # Phase 2: Execute scenes
        self.scene_1_introduction()
        self.scene_2_construction()
    
    def setup_geometry(self):
        """Calculate all points, lengths, angles ONCE"""
        # Base vertices
        self.A = np.array([-2, -1, 0])
        self.B = np.array([2, -1, 0])
        self.C = np.array([0, 2, 0])
        
        # Derived points - CALCULATED, not guessed
        self.M_AB = (self.A + self.B) / 2
        self.circumcenter = self.calc_circumcenter(self.A, self.B, self.C)
        
        # Verify correctness
        self.verify_geometry()
```

### Calculation Library

Use the provided geometry calculator (see `references/geometry-calculations.md`):

```python
from references.geometry_calculator import GeometryCalculator as GC

# Perpendicular foot
foot = GC.perpendicular_foot(point, line_start, line_end)

# Line intersection
intersection = GC.line_intersection(P1, dir1, P2, dir2)

# Triangle centers
circumcenter = GC.circumcenter(A, B, C)
incenter = GC.incenter(A, B, C)
```

### Verification System

```python
def verify_geometry(self):
    """Run after setup_geometry()"""
    epsilon = 1e-6
    
    # Example: Verify circumcenter equidistant from vertices
    r_A = np.linalg.norm(self.A - self.circumcenter)
    r_B = np.linalg.norm(self.B - self.circumcenter)
    r_C = np.linalg.norm(self.C - self.circumcenter)
    
    assert abs(r_A - r_B) < epsilon, f"Circumcenter error: {r_A} ≠ {r_B}"
    assert abs(r_B - r_C) < epsilon, f"Circumcenter error: {r_B} ≠ {r_C}"
```

## Angle Creation (Manim 0.19.2)

### Using Angle.from_three_points (Recommended)

```python
# Create angle ∠ABC (B is vertex)
angle = Angle.from_three_points(
    A,  # Point on first ray
    B,  # Vertex
    C,  # Point on second ray
    radius=0.5,
    quadrant=(1, 1)  # Adjust based on position
)
```

### Quadrant Parameter Guide

- `quadrant=(1, 1)` - Both lines' end sides (default)
- `quadrant=(-1, 1)` - Line1 start side, Line2 end side
- `quadrant=(1, -1)` - Line1 end side, Line2 start side
- `quadrant=(-1, -1)` - Both lines' start sides

### Direction Control

```python
# Determine if angle needs other_angle
v1 = point1 - vertex
v2 = point2 - vertex
cross_z = v1[0] * v2[1] - v1[1] * v2[0]

if cross_z > 0:
    # Counter-clockwise: use default
    angle = Angle(line1, line2, other_angle=False)
else:
    # Clockwise: use other_angle
    angle = Angle(line1, line2, other_angle=True)
```

### Right Angles

```python
# Method 1: RightAngle class
right_angle = RightAngle(line1, line2, length=0.3, quadrant=(1,1))

# Method 2: Angle with elbow
angle = Angle(line1, line2, radius=0.3, elbow=True)
```

## TikTok Vertical Format

### Canvas Setup

```python
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16

# Coordinate system (logical units):
# x: [-4.5, +4.5], safe zone: [-4, +4]
# y: [-8, +8], zones:
#   [+5.5, +8]: Title/author area
#   [-3, +5]: Main content area
#   [-6, -3]: Text/explanation area
#   [-8, -6]: Bottom safe zone
```

### Font Sizes

```python
FONT_SIZES = {
    "title": 36,
    "subtitle": 28,
    "body": 22,
    "label": 20,
    "formula": 28,
}
```

### Branding Template

```python
author_info = Text(
    "上海初高中数学直通车 @emptyandcalm",
    font="Noto Sans CJK SC",
    font_size=20,
    color=GRAY_B
).move_to(UP * 7)
```

## Animation Timing Guide

| Content Type | Duration | Example |
|--------------|----------|---------|
| Simple shape | 0.5-1.0s | `Create(line)` |
| Complex shape | 1.0-1.5s | `Create(triangle)` |
| Text write | 0.4-0.8s | `Write(text)` |
| Formula | 0.6-1.0s | `Write(formula)` |
| Transform | 0.8-1.2s | `Transform(a, b)` |
| **Key concept pause** | **2.0-3.0s** | After crucial step |
| Transition | 0.4-0.6s | Between scenes |

**Principle:** Slow for difficult concepts, fast for simple steps.

## References

For detailed information, see:

- `references/geometry-calculations.md` - Complete calculation library
- `references/manim-constraints.md` - All version-specific constraints
- `references/storyboard-template.md` - Planning template
- `references/timing-guide.md` - Animation pacing details
- `references/troubleshooting.md` - Common errors and fixes

## Complete Example

See `scripts/triangle_five_centers.py` for a production-ready example demonstrating:
- Unified geometry initialization
- Verification system
- Correct angle creation
- Chinese text handling
- TikTok vertical format
- Proper animation pacing

## Render Commands

```bash
# Quick preview
manim -pql script.py SceneName

# High quality
manim -qh script.py SceneName

# 4K production
manim -qk script.py SceneName
```
