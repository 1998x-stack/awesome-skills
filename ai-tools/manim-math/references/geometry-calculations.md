# Geometry Calculations Library

Complete reference for precise geometric calculations in Manim animations.

## Core Principles

1. **Never guess coordinates** - Calculate everything
2. **Use NumPy** - All vector operations
3. **Verify results** - Check relationships hold

## GeometryCalculator Class

```python
import numpy as np

class GeometryCalculator:
    """Precise geometry calculations for Manim"""
    
    @staticmethod
    def midpoint(P1, P2):
        """Calculate midpoint between two points"""
        return (P1 + P2) / 2
    
    @staticmethod
    def perpendicular_foot(point, line_start, line_end):
        """
        Calculate foot of perpendicular from point to line
        
        Args:
            point: Point to project
            line_start, line_end: Define the line
        
        Returns:
            Foot of perpendicular (np.array)
        """
        line_vec = line_end - line_start
        point_vec = point - line_start
        t = np.dot(point_vec, line_vec) / np.dot(line_vec, line_vec)
        return line_start + t * line_vec
    
    @staticmethod
    def line_intersection(P1, D1, P2, D2):
        """
        Calculate intersection of two lines
        Line 1: P1 + t*D1
        Line 2: P2 + s*D2
        
        Returns:
            Intersection point or None if parallel
        """
        A = np.array([[D1[0], -D2[0]], [D1[1], -D2[1]]])
        b = np.array([P2[0] - P1[0], P2[1] - P1[1]])
        
        if np.abs(np.linalg.det(A)) < 1e-10:
            return None  # Parallel lines
        
        params = np.linalg.solve(A, b)
        return np.array([*(P1[:2] + params[0] * D1[:2]), 0])
    
    @staticmethod
    def circumcenter(A, B, C):
        """
        Calculate triangle circumcenter (equidistant from all vertices)
        
        Formula: Intersection of perpendicular bisectors
        """
        ax, ay = A[0], A[1]
        bx, by = B[0], B[1]
        cx, cy = C[0], C[1]
        
        D = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
        
        if abs(D) < 1e-10:
            return (A + B + C) / 3  # Degenerate case
        
        ux = ((ax**2+ay**2)*(by-cy) + (bx**2+by**2)*(cy-ay) + (cx**2+cy**2)*(ay-by)) / D
        uy = ((ax**2+ay**2)*(cx-bx) + (bx**2+by**2)*(ax-cx) + (cx**2+cy**2)*(bx-ax)) / D
        
        return np.array([ux, uy, 0])
    
    @staticmethod
    def incenter(A, B, C):
        """
        Calculate triangle incenter (equidistant from all sides)
        
        Formula: Weighted average by opposite side lengths
        """
        a = np.linalg.norm(B - C)  # BC
        b = np.linalg.norm(C - A)  # CA
        c = np.linalg.norm(A - B)  # AB
        return (a*A + b*B + c*C) / (a + b + c)
    
    @staticmethod
    def centroid(A, B, C):
        """Calculate triangle centroid (center of mass)"""
        return (A + B + C) / 3
    
    @staticmethod
    def orthocenter(A, B, C):
        """
        Calculate triangle orthocenter (intersection of altitudes)
        
        Method: Intersection of two altitude lines
        """
        ax, ay = A[0], A[1]
        bx, by = B[0], B[1]
        cx, cy = C[0], C[1]
        
        # Altitude from A perpendicular to BC
        # Altitude from B perpendicular to AC
        
        det = (cy - by) * (ax - cx) - (bx - cx) * (cy - ay)
        
        if abs(det) < 1e-10:
            return (A + B + C) / 3  # Degenerate
        
        t1 = ((bx - ax) * (ax - cx) + (by - ay) * (ay - cy)) / det
        
        hx = ax + t1 * (cy - by)
        hy = ay + t1 * (bx - cx)
        
        return np.array([hx, hy, 0])
    
    @staticmethod
    def excenter_A(A, B, C):
        """
        Calculate excenter opposite to vertex A
        
        Formula: J_A = (-a*A + b*B + c*C) / (-a + b + c)
        """
        a = np.linalg.norm(B - C)
        b = np.linalg.norm(C - A)
        c = np.linalg.norm(A - B)
        
        denom = -a + b + c
        if abs(denom) < 1e-10:
            return A + (B - A) * 2  # Fallback
        
        return (-a*A + b*B + c*C) / denom
    
    @staticmethod
    def angle_between_vectors(V1, V2):
        """Calculate angle between two vectors (radians)"""
        cos_angle = np.dot(V1, V2) / (np.linalg.norm(V1) * np.linalg.norm(V2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        return np.arccos(cos_angle)
    
    @staticmethod
    def angle_at_vertex(A, B, C):
        """
        Calculate angle ∠ABC (B is vertex)
        
        Returns: Angle in radians
        """
        BA = A - B
        BC = C - B
        return GeometryCalculator.angle_between_vectors(BA, BC)
    
    @staticmethod
    def distance_point_to_line(point, line_start, line_end):
        """Calculate perpendicular distance from point to line"""
        line_vec = line_end - line_start
        point_vec = point - line_start
        cross_product = np.cross(point_vec[:2], line_vec[:2])
        return np.abs(cross_product) / np.linalg.norm(line_vec)
    
    @staticmethod
    def perpendicular_bisector(P1, P2):
        """
        Calculate perpendicular bisector of segment P1P2
        
        Returns: (midpoint, perpendicular_direction)
        """
        midpoint = (P1 + P2) / 2
        segment = P2 - P1
        perpendicular = np.array([-segment[1], segment[0], 0])
        return midpoint, perpendicular
    
    @staticmethod
    def reflection_point(point, line_start, line_end):
        """Calculate reflection of point across line"""
        foot = GeometryCalculator.perpendicular_foot(point, line_start, line_end)
        return 2 * foot - point
    
    @staticmethod
    def parallel_line_through_point(point, line_start, line_end, length=2):
        """Create line parallel to given line, passing through point"""
        direction = line_end - line_start
        direction = direction / np.linalg.norm(direction)
        return point - length/2 * direction, point + length/2 * direction
    
    @staticmethod
    def perpendicular_line_through_point(point, line_start, line_end, length=2):
        """Create line perpendicular to given line, passing through point"""
        line_vec = line_end - line_start
        perp_vec = np.array([-line_vec[1], line_vec[0], 0])
        perp_vec = perp_vec / np.linalg.norm(perp_vec)
        return point - length/2 * perp_vec, point + length/2 * perp_vec
```

## Verification Functions

```python
def verify_collinear(P1, P2, P3, epsilon=1e-6):
    """Verify three points are collinear"""
    area = 0.5 * abs(
        P1[0]*(P2[1]-P3[1]) + 
        P2[0]*(P3[1]-P1[1]) + 
        P3[0]*(P1[1]-P2[1])
    )
    return area < epsilon

def verify_perpendicular(line1_vec, line2_vec, epsilon=1e-6):
    """Verify two vectors are perpendicular"""
    dot_product = np.dot(line1_vec[:2], line2_vec[:2])
    return abs(dot_product) < epsilon

def verify_parallel(line1_vec, line2_vec, epsilon=1e-6):
    """Verify two vectors are parallel"""
    cross = np.cross(line1_vec[:2], line2_vec[:2])
    return abs(cross) < epsilon

def verify_distances_equal(distances, epsilon=1e-6):
    """Verify all distances in list are equal"""
    if len(distances) < 2:
        return True
    ref = distances[0]
    return all(abs(d - ref) < epsilon for d in distances)
```

## Usage Example

```python
from manim import *
import numpy as np

class PreciseTriangle(Scene):
    def setup_geometry(self):
        # Define base triangle
        self.A = np.array([-2, -1, 0])
        self.B = np.array([2, -1, 0])
        self.C = np.array([0, 2, 0])
        
        # Calculate centers
        calc = GeometryCalculator
        self.O = calc.circumcenter(self.A, self.B, self.C)
        self.I = calc.incenter(self.A, self.B, self.C)
        self.G = calc.centroid(self.A, self.B, self.C)
        self.H = calc.orthocenter(self.A, self.B, self.C)
        
        # Verify circumcenter
        distances = [
            np.linalg.norm(self.O - self.A),
            np.linalg.norm(self.O - self.B),
            np.linalg.norm(self.O - self.C)
        ]
        assert verify_distances_equal(distances), "Circumcenter calculation error"
```

## Common Patterns

### Finding Division Point

```python
def divide_segment(P1, P2, ratio):
    """
    Divide segment P1P2 in ratio m:n
    ratio = m / (m + n)
    """
    return P1 + ratio * (P2 - P1)

# Example: Find 2:1 division point
point = divide_segment(A, B, 2/3)  # AP:PB = 2:1
```

### Angle Bisector Endpoint

```python
def angle_bisector_point(vertex, point1, point2, length=2):
    """Calculate point on angle bisector"""
    v1 = (point1 - vertex) / np.linalg.norm(point1 - vertex)
    v2 = (point2 - vertex) / np.linalg.norm(point2 - vertex)
    bisector_dir = v1 + v2
    bisector_dir = bisector_dir / np.linalg.norm(bisector_dir)
    return vertex + length * bisector_dir
```

### Circle Through Three Points

```python
def circle_through_points(A, B, C):
    """Calculate circle parameters from three points"""
    center = GeometryCalculator.circumcenter(A, B, C)
    radius = np.linalg.norm(A - center)
    return center, radius
```
