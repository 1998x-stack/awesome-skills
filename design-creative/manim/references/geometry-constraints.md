# Geometry Constraints Reference

Precise calculation library for Manim geometric animations.

## Core Principle

> **ALL geometric elements must be calculated via NumPy. NEVER guess coordinates!**

## Geometry Calculator Class

```python
import numpy as np

class GeometryCalculator:
    """Utility class for precise geometric calculations"""
    
    @staticmethod
    def midpoint(P1, P2):
        """Midpoint of segment P1P2"""
        return (P1 + P2) / 2
    
    @staticmethod
    def foot_of_perpendicular(point, line_start, line_end):
        """Perpendicular foot from point to line"""
        line_vec = line_end - line_start
        point_vec = point - line_start
        t = np.dot(point_vec, line_vec) / np.dot(line_vec, line_vec)
        return line_start + t * line_vec
    
    @staticmethod
    def line_intersection(P1, D1, P2, D2):
        """
        Intersection of two lines
        Line1: P1 + t*D1, Line2: P2 + s*D2
        Returns None if parallel
        """
        A = np.array([[D1[0], -D2[0]], [D1[1], -D2[1]]])
        b = np.array([P2[0] - P1[0], P2[1] - P1[1]])
        if np.abs(np.linalg.det(A)) < 1e-10:
            return None
        params = np.linalg.solve(A, b)
        return np.array([*(P1[:2] + params[0] * D1[:2]), 0])
    
    @staticmethod
    def circumcenter(A, B, C):
        """Triangle circumcenter (equidistant from all vertices)"""
        ax, ay = A[0], A[1]
        bx, by = B[0], B[1]
        cx, cy = C[0], C[1]
        D = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
        ux = ((ax**2+ay**2)*(by-cy) + (bx**2+by**2)*(cy-ay) + (cx**2+cy**2)*(ay-by)) / D
        uy = ((ax**2+ay**2)*(cx-bx) + (bx**2+by**2)*(ax-cx) + (cx**2+cy**2)*(bx-ax)) / D
        return np.array([ux, uy, 0])
    
    @staticmethod
    def incenter(A, B, C):
        """Triangle incenter (equidistant from all sides)"""
        a = np.linalg.norm(B - C)
        b = np.linalg.norm(C - A)
        c = np.linalg.norm(A - B)
        return (a*A + b*B + c*C) / (a + b + c)
    
    @staticmethod
    def centroid(A, B, C):
        """Triangle centroid (center of mass)"""
        return (A + B + C) / 3
    
    @staticmethod
    def orthocenter(A, B, C):
        """Triangle orthocenter (altitude intersection)"""
        O = GeometryCalculator.circumcenter(A, B, C)
        return A + B + C - 2*O
    
    @staticmethod
    def angle_between(V1, V2):
        """Angle between vectors (radians)"""
        cos_angle = np.dot(V1, V2) / (np.linalg.norm(V1) * np.linalg.norm(V2))
        return np.arccos(np.clip(cos_angle, -1.0, 1.0))
    
    @staticmethod
    def angle_at_vertex(A, B, C):
        """Angle ABC at vertex B (radians)"""
        return GeometryCalculator.angle_between(A - B, C - B)
    
    @staticmethod
    def distance_point_to_line(point, line_start, line_end):
        """Distance from point to line"""
        line_vec = line_end - line_start
        point_vec = point - line_start
        cross = np.cross(point_vec[:2], line_vec[:2])
        return np.abs(cross) / np.linalg.norm(line_vec)
    
    @staticmethod
    def perpendicular_bisector(P1, P2):
        """Perpendicular bisector: returns (midpoint, direction_vector)"""
        mid = (P1 + P2) / 2
        segment = P2 - P1
        perp = np.array([-segment[1], segment[0], 0])
        return mid, perp
    
    @staticmethod
    def reflection_point(point, line_start, line_end):
        """Reflection of point across line"""
        foot = GeometryCalculator.foot_of_perpendicular(point, line_start, line_end)
        return 2 * foot - point
    
    @staticmethod
    def triangle_area(A, B, C):
        """Triangle area using cross product"""
        return 0.5 * np.abs(
            A[0]*(B[1]-C[1]) + B[0]*(C[1]-A[1]) + C[0]*(A[1]-B[1])
        )
    
    @staticmethod
    def are_collinear(P1, P2, P3, eps=1e-10):
        """Check if three points are collinear"""
        area = GeometryCalculator.triangle_area(P1, P2, P3)
        return area < eps
    
    @staticmethod
    def are_perpendicular(V1, V2, eps=1e-10):
        """Check if two vectors are perpendicular"""
        return abs(np.dot(V1[:2], V2[:2])) < eps
    
    @staticmethod
    def are_parallel(V1, V2, eps=1e-10):
        """Check if two vectors are parallel"""
        cross = np.cross(V1[:2], V2[:2])
        return abs(cross) < eps
```

## Scene Structure Pattern

```python
class PreciseGeometryScene(Scene):
    def construct(self):
        self.setup_geometry()      # 1. Calculate all coordinates
        self.create_objects()      # 2. Create Manim objects
        self.verify_geometry()     # 3. Validate relationships
        self.animate()             # 4. Run animations
    
    def setup_geometry(self):
        """Initialize ALL coordinates here - never recalculate"""
        # Base parameters
        self.SCALE = 1.0
        self.OFFSET = ORIGIN
        
        # Primary vertices
        self.A = np.array([-2, -1, 0]) * self.SCALE + self.OFFSET
        self.B = np.array([2, -1, 0]) * self.SCALE + self.OFFSET
        self.C = np.array([0, 2, 0]) * self.SCALE + self.OFFSET
        
        # Derived points (calculate once!)
        self.M_AB = (self.A + self.B) / 2
        self.circumcenter = GeometryCalculator.circumcenter(self.A, self.B, self.C)
        
        # Cache lengths
        self.AB = np.linalg.norm(self.B - self.A)
        self.BC = np.linalg.norm(self.C - self.B)
        self.CA = np.linalg.norm(self.A - self.C)
    
    def verify_geometry(self):
        """Validate geometric relationships"""
        eps = 1e-6
        
        # Verify circumcenter equidistant from vertices
        r_A = np.linalg.norm(self.A - self.circumcenter)
        r_B = np.linalg.norm(self.B - self.circumcenter)
        r_C = np.linalg.norm(self.C - self.circumcenter)
        
        assert abs(r_A - r_B) < eps, "Circumcenter error"
        assert abs(r_B - r_C) < eps, "Circumcenter error"
        
        print("✓ Geometry verified")
```

## Angle Creation Guide

### The Angle Class Parameters

```python
Angle(
    line1, line2,         # Two Line objects
    radius=0.5,           # Arc radius
    quadrant=(1, 1),      # Anchor selection
    other_angle=False,    # Complementary angle toggle
    dot=False,            # Show dot (for right angles)
    elbow=False           # Use elbow symbol (right angles)
)
```

### Understanding quadrant

The `quadrant` parameter `(a, b)` controls where the angle arc anchors:
- `a = 1`: Use line1's END point
- `a = -1`: Use line1's START point  
- `b = 1`: Use line2's END point
- `b = -1`: Use line2's START point

### Angle Direction Logic

```python
def create_angle_arc(vertex, point1, point2, radius=0.5):
    """
    Create angle arc from point1 to point2 at vertex
    Automatically handles direction
    """
    line1 = Line(vertex, point1)
    line2 = Line(vertex, point2)
    
    # Calculate cross product to determine direction
    v1 = point1 - vertex
    v2 = point2 - vertex
    cross_z = v1[0] * v2[1] - v1[1] * v2[0]
    
    # cross_z > 0: counterclockwise (use default)
    # cross_z < 0: clockwise (use other_angle=True)
    other_angle = cross_z < 0
    
    return Angle(line1, line2, radius=radius, other_angle=other_angle)
```

### Using from_three_points (Recommended)

```python
# Angle at vertex B (angle ABC)
angle = Angle.from_three_points(
    A,              # Point on first ray
    B,              # Vertex
    C,              # Point on second ray
    radius=0.5,
    other_angle=False
)
```

## Circle Calculations

```python
@staticmethod
def circle_intersection(c1, r1, c2, r2):
    """Find intersection points of two circles"""
    d = np.linalg.norm(c2[:2] - c1[:2])
    
    if d > r1 + r2 or d < abs(r1 - r2):
        return []  # No intersection
    
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h = np.sqrt(max(0, r1**2 - a**2))
    
    direction = (c2 - c1) / d
    perpendicular = np.array([-direction[1], direction[0], 0])
    
    midpoint = c1 + a * direction
    
    if h < 1e-10:
        return [midpoint]  # Tangent
    
    return [
        midpoint + h * perpendicular,
        midpoint - h * perpendicular
    ]

@staticmethod
def tangent_points_from_external(point, center, radius):
    """Find tangent points from external point to circle"""
    d = np.linalg.norm(point[:2] - center[:2])
    
    if d < radius:
        return []  # Point inside circle
    
    if abs(d - radius) < 1e-10:
        return [point.copy()]  # Point on circle
    
    # Distance from center to tangent point along center-point line
    a = radius**2 / d
    h = np.sqrt(radius**2 - a**2)
    
    direction = (point - center) / d
    perpendicular = np.array([-direction[1], direction[0], 0])
    
    base = center + a * direction
    
    return [
        base + h * perpendicular,
        base - h * perpendicular
    ]
```

## Common Error Prevention

### Scale Synchronization

```python
# ❌ WRONG: Derived points not updated after scale
triangle = Polygon(A, B, C)
triangle.scale(0.5)
dot.move_to(self.circumcenter)  # WRONG! Still uses old position

# ✅ CORRECT: Use always_redraw for auto-update
circumcenter_dot = always_redraw(lambda: Dot(
    GeometryCalculator.circumcenter(
        *self.triangle.get_vertices()[:3]
    )
))

# ✅ ALTERNATIVE: Recalculate after transformation
old_center = triangle.get_center()
triangle.scale(0.5)
new_center = triangle.get_center()
scale_factor = 0.5
new_circumcenter = (self.circumcenter - old_center) * scale_factor + new_center
dot.move_to(new_circumcenter)
```

### Angle Direction Determination

```python
def determine_angle_direction(vertex, point_a, point_b):
    """
    Determine rotation direction from point_a to point_b around vertex
    Returns: 'CCW' (counterclockwise) or 'CW' (clockwise)
    """
    v1 = np.array(point_a) - np.array(vertex)
    v2 = np.array(point_b) - np.array(vertex)
    
    # 2D cross product (z-component)
    cross_z = v1[0] * v2[1] - v1[1] * v2[0]
    
    return 'CCW' if cross_z > 0 else 'CW'

def create_angle_with_correct_direction(vertex, point_a, point_b, radius=0.5, 
                                         desired_direction='CCW'):
    """Create angle arc with specified direction"""
    actual = determine_angle_direction(vertex, point_a, point_b)
    other_angle = (actual != desired_direction)
    
    line1 = Line(vertex, point_a)
    line2 = Line(vertex, point_b)
    return Angle(line1, line2, radius=radius, other_angle=other_angle)
```

### Numerical Stability

```python
class NumericalSafety:
    """Safe numerical operations"""
    
    @staticmethod
    def safe_arccos(x):
        """arccos with boundary handling"""
        return np.arccos(np.clip(x, -1.0, 1.0))
    
    @staticmethod
    def safe_divide(a, b, default=0):
        """Division with zero check"""
        return default if abs(b) < 1e-15 else a / b
    
    @staticmethod
    def safe_normalize(v):
        """Vector normalization with zero check"""
        norm = np.linalg.norm(v)
        return v if norm < 1e-15 else v / norm
    
    @staticmethod
    def float_equal(a, b, eps=1e-10):
        """Safe float comparison"""
        return abs(a - b) < eps
```

### Boundary Checking

```python
# Scene bounds: approximately -7 to 7 (x), -4 to 4 (y)
SAFE_X = 6.5
SAFE_Y = 3.5

def clamp_to_bounds(position):
    return np.array([
        np.clip(position[0], -SAFE_X, SAFE_X),
        np.clip(position[1], -SAFE_Y, SAFE_Y),
        0
    ])
```

## Verification Checklist

Before running animation:
- [ ] All coordinates calculated mathematically (no guessing)
- [ ] Derived points calculated from primary points
- [ ] Perpendicular relationships verified with dot product = 0
- [ ] Parallel relationships verified with cross product = 0
- [ ] Angle sums equal expected values
- [ ] All objects within scene bounds

### Quick Verification Functions

```python
def verify_triangle_geometry(A, B, C, eps=1e-6):
    """Verify basic triangle properties"""
    # Calculate angles
    angle_A = GeometryCalculator.angle_at_vertex(B, A, C)
    angle_B = GeometryCalculator.angle_at_vertex(C, B, A)
    angle_C = GeometryCalculator.angle_at_vertex(A, C, B)
    
    # Angle sum should be PI
    angle_sum = angle_A + angle_B + angle_C
    assert abs(angle_sum - PI) < eps, f"Angle sum error: {angle_sum} != PI"
    
    # Circumcenter equidistant from vertices
    O = GeometryCalculator.circumcenter(A, B, C)
    r_A = np.linalg.norm(A - O)
    r_B = np.linalg.norm(B - O)
    r_C = np.linalg.norm(C - O)
    
    assert abs(r_A - r_B) < eps, "Circumcenter distance error"
    assert abs(r_B - r_C) < eps, "Circumcenter distance error"
    
    print("✓ Triangle geometry verified")
    return True

def verify_perpendicular(line1_start, line1_end, line2_start, line2_end, eps=1e-8):
    """Verify two lines are perpendicular"""
    v1 = np.array(line1_end) - np.array(line1_start)
    v2 = np.array(line2_end) - np.array(line2_start)
    dot = np.dot(v1[:2], v2[:2])
    
    assert abs(dot) < eps, f"Not perpendicular: dot product = {dot}"
    return True

def verify_parallel(line1_start, line1_end, line2_start, line2_end, eps=1e-8):
    """Verify two lines are parallel"""
    v1 = np.array(line1_end) - np.array(line1_start)
    v2 = np.array(line2_end) - np.array(line2_start)
    cross = np.cross(v1[:2], v2[:2])
    
    assert abs(cross) < eps, f"Not parallel: cross product = {cross}"
    return True
```

### Common Manim 0.19.2 Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `inner_radius` on Sector | Sector only uses `radius` | Use AnnularSector for rings |
| `corner_radius` on Rectangle | Rectangle has no corner_radius | Use RoundedRectangle |
| Unicode in MathTex | MathTex doesn't support Unicode | Use Text with font parameter |
| `°` in LaTeX | Special character | Use `^\circ` |
| `{{a}\over{b}}` | Double braces parsing error | Use `\frac{a}{b}` |
| Positional args in SurroundingRectangle | API change in 0.19 | Use keyword arguments |
