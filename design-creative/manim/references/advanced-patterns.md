# Advanced Manim Patterns

## Complex Equation Transforms

### Multi-step Derivation with Highlights

```python
class Derivation(Scene):
    def construct(self):
        steps = [
            MathTex(r"(a+b)^2"),
            MathTex(r"(a+b)(a+b)"),
            MathTex(r"a \cdot a + a \cdot b + b \cdot a + b \cdot b"),
            MathTex(r"a^2 + ab + ba + b^2"),
            MathTex(r"a^2 + 2ab + b^2"),
        ]
        
        current = steps[0].to_edge(UP)
        self.play(Write(current))
        
        for next_step in steps[1:]:
            next_step.move_to(current)
            self.play(TransformMatchingTex(current, next_step))
            self.wait(0.5)
            current = next_step
```

### Isolating and Transforming Subexpressions

```python
eq1 = MathTex("2", "x", "+", "3", "=", "7")
eq2 = MathTex("2", "x", "=", "7", "-", "3")
eq3 = MathTex("2", "x", "=", "4")
eq4 = MathTex("x", "=", "2")

# Color the parts being manipulated
eq1[3].set_color(YELLOW)  # "3"
eq2[3:6].set_color(YELLOW)  # "7-3"

self.play(TransformMatchingTex(eq1, eq2))
```

## Dynamic Graph Animations

### Parametric Curve Tracing

```python
class ParametricTrace(Scene):
    def construct(self):
        axes = Axes(x_range=[-4, 4], y_range=[-4, 4])
        t = ValueTracker(0)
        
        # Parametric equations: x = cos(t), y = sin(2t)
        dot = always_redraw(lambda: Dot(
            axes.c2p(np.cos(t.get_value()), np.sin(2 * t.get_value())),
            color=RED
        ))
        
        path = TracedPath(dot.get_center, stroke_color=BLUE, stroke_width=2)
        
        self.add(axes, path, dot)
        self.play(t.animate.set_value(2 * PI), run_time=6, rate_func=linear)
```

### Multiple Functions Comparison

```python
class FunctionComparison(Scene):
    def construct(self):
        axes = Axes(x_range=[-3, 3], y_range=[-2, 5])
        
        funcs = [
            (lambda x: x, "x", BLUE),
            (lambda x: x**2, "x^2", RED),
            (lambda x: x**3, "x^3", GREEN),
        ]
        
        graphs = VGroup()
        labels = VGroup()
        
        for func, tex, color in funcs:
            graph = axes.plot(func, color=color)
            label = axes.get_graph_label(graph, tex, x_val=2)
            graphs.add(graph)
            labels.add(label)
        
        self.play(Create(axes))
        for g, l in zip(graphs, labels):
            self.play(Create(g), Write(l))
            self.wait(0.5)
```

### Animated Function Parameters

```python
class AnimatedSine(Scene):
    def construct(self):
        axes = Axes(x_range=[-PI, PI], y_range=[-2, 2])
        
        freq = ValueTracker(1)
        amp = ValueTracker(1)
        
        graph = always_redraw(lambda: axes.plot(
            lambda x: amp.get_value() * np.sin(freq.get_value() * x),
            color=BLUE
        ))
        
        freq_label = always_redraw(lambda: MathTex(
            f"f = {freq.get_value():.1f}"
        ).to_corner(UR))
        
        self.add(axes, graph, freq_label)
        self.play(freq.animate.set_value(3), run_time=3)
        self.play(amp.animate.set_value(0.5), run_time=2)
```

## Geometric Constructions

### Angle Animation with Labels

```python
class AngleDemo(Scene):
    def construct(self):
        line1 = Line(ORIGIN, RIGHT * 2)
        line2 = Line(ORIGIN, RIGHT * 2)
        
        theta = ValueTracker(30)
        
        line2.add_updater(
            lambda m: m.become(
                Line(ORIGIN, RIGHT * 2).rotate(theta.get_value() * DEGREES, about_point=ORIGIN)
            )
        )
        
        angle = always_redraw(lambda: Angle(line1, line2, radius=0.5))
        label = always_redraw(lambda: MathTex(
            f"{theta.get_value():.0f}^\\circ"
        ).move_to(Angle(line1, line2, radius=0.8).point_from_proportion(0.5)))
        
        self.add(line1, line2, angle, label)
        self.play(theta.animate.set_value(120), run_time=3)
```

### Circle Theorems

```python
class InscribedAngle(Scene):
    def construct(self):
        circle = Circle(radius=2, color=WHITE)
        
        # Points on circle
        A = circle.point_at_angle(0)
        B = circle.point_at_angle(PI * 2/3)
        C = circle.point_at_angle(PI * 4/3)
        
        # Inscribed triangle
        triangle = Polygon(A, B, C, color=BLUE)
        
        # Labels
        labels = VGroup(
            Tex("A").next_to(A, RIGHT),
            Tex("B").next_to(B, UL),
            Tex("C").next_to(C, DL),
        )
        
        self.play(Create(circle))
        self.play(Create(triangle), Write(labels))
```

## Matrix and Linear Algebra

### Matrix Transformation Visualization

```python
class MatrixVis(LinearTransformationScene):
    def __init__(self):
        LinearTransformationScene.__init__(
            self,
            show_coordinates=True,
            leave_ghost_vectors=True,
        )
    
    def construct(self):
        matrix = [[2, 1], [1, 2]]
        
        v1 = self.add_vector([1, 0], color=RED)
        v2 = self.add_vector([0, 1], color=BLUE)
        
        self.apply_matrix(matrix)
        self.wait()
```

### Eigenvector Animation

```python
class EigenvectorDemo(Scene):
    def construct(self):
        plane = NumberPlane()
        
        matrix = np.array([[3, 1], [0, 2]])
        eigvals, eigvecs = np.linalg.eig(matrix)
        
        vectors = VGroup()
        for i, (val, vec) in enumerate(zip(eigvals, eigvecs.T)):
            v = Arrow(ORIGIN, vec * 2, color=[RED, BLUE][i], buff=0)
            label = MathTex(f"\\lambda_{i+1} = {val:.1f}").next_to(v, UP)
            vectors.add(VGroup(v, label))
        
        self.add(plane)
        self.play(*[GrowArrow(v[0]) for v in vectors])
        self.play(*[Write(v[1]) for v in vectors])
```

## Text and Annotations

### Brace with Label

```python
line = Line(LEFT * 2, RIGHT * 2)
brace = Brace(line, DOWN)
label = brace.get_tex("L = 4")

self.play(Create(line))
self.play(GrowFromCenter(brace), Write(label))
```

### SurroundingRectangle for Highlighting

```python
eq = MathTex("a^2", "+", "b^2", "=", "c^2")
box1 = SurroundingRectangle(eq[0], color=RED)
box2 = SurroundingRectangle(eq[2], color=BLUE)

self.play(Create(box1))
self.play(ReplacementTransform(box1, box2))
```

### Numbered Equations

```python
class NumberedEqs(Scene):
    def construct(self):
        eqs = VGroup(
            MathTex(r"F = ma"),
            MathTex(r"E = mc^2"),
            MathTex(r"p = mv"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        
        for i, eq in enumerate(eqs, 1):
            num = MathTex(f"({i})").next_to(eq, RIGHT, buff=1)
            eq.add(num)
        
        self.play(LaggedStart(*[Write(eq) for eq in eqs], lag_ratio=0.3))
```

## Animation Sequences

### LaggedStart for Staggered Animations

```python
dots = VGroup(*[Dot() for _ in range(10)]).arrange(RIGHT)

# Staggered fade in
self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.1))

# Staggered scale
self.play(LaggedStart(*[d.animate.scale(2) for d in dots], lag_ratio=0.05))
```

### AnimationGroup for Simultaneous Animations

```python
self.play(AnimationGroup(
    Create(circle),
    Write(label),
    FadeIn(background),
    lag_ratio=0  # All simultaneous
))
```

### Succession for Sequential Animations

```python
self.play(Succession(
    FadeIn(obj1),
    obj1.animate.shift(UP),
    FadeIn(obj2),
    obj2.animate.shift(DOWN),
))
```

## Camera Techniques (2D)

### Zooming

```python
class ZoomScene(MovingCameraScene):
    def construct(self):
        circle = Circle()
        dot = Dot(circle.get_center())
        
        self.add(circle, dot)
        
        # Zoom in
        self.play(self.camera.frame.animate.scale(0.5).move_to(dot))
        self.wait()
        
        # Zoom out
        self.play(self.camera.frame.animate.scale(2).move_to(ORIGIN))
```

### Frame Movement

```python
class MovingCamera(MovingCameraScene):
    def construct(self):
        objects = VGroup(*[Circle().shift(RIGHT * i * 3) for i in range(5)])
        self.add(objects)
        
        for obj in objects:
            self.play(self.camera.frame.animate.move_to(obj))
            self.wait(0.5)
```

## Custom Mobjects

### Creating a Custom Shape

```python
class RightAngle(VMobject):
    def __init__(self, line1, line2, size=0.3, **kwargs):
        super().__init__(**kwargs)
        
        # Get the corner point
        corner = line_intersection(
            [line1.get_start(), line1.get_end()],
            [line2.get_start(), line2.get_end()]
        )
        
        # Create the right angle marker
        v1 = normalize(line1.get_end() - corner)
        v2 = normalize(line2.get_end() - corner)
        
        self.set_points_as_corners([
            corner + v1 * size,
            corner + v1 * size + v2 * size,
            corner + v2 * size,
        ])
```

## Performance Tips

1. **Use `always_redraw` wisely** - Only for objects that truly need per-frame updates
2. **Remove unused objects** - `self.remove(obj)` frees memory
3. **Batch similar operations** - Use `VGroup` for collective transforms
4. **Cache complex calculations** - Store in variables, don't recalculate
5. **Lower quality for development** - Always use `-ql` until final render
