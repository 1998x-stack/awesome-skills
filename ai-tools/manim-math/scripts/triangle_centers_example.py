"""
Triangle Centers Example - Demonstrates Best Practices
Professional math animation for middle school geometry
"""

from manim import *
import numpy as np

# TikTok vertical format
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16


class GeometryCalculator:
    """Precise geometry calculations"""
    
    @staticmethod
    def circumcenter(A, B, C):
        ax, ay = A[0], A[1]
        bx, by = B[0], B[1]
        cx, cy = C[0], C[1]
        D = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
        if abs(D) < 1e-10:
            return (A + B + C) / 3
        ux = ((ax**2+ay**2)*(by-cy) + (bx**2+by**2)*(cy-ay) + (cx**2+cy**2)*(ay-by)) / D
        uy = ((ax**2+ay**2)*(cx-bx) + (bx**2+by**2)*(ax-cx) + (cx**2+cy**2)*(bx-ax)) / D
        return np.array([ux, uy, 0])
    
    @staticmethod
    def incenter(A, B, C):
        a = np.linalg.norm(B - C)
        b = np.linalg.norm(C - A)
        c = np.linalg.norm(A - B)
        return (a*A + b*B + c*C) / (a + b + c)


class TriangleCentersDemo(Scene):
    """Demonstrates circumcenter and incenter with verification"""
    
    def construct(self):
        self.camera.background_color = "#1a1a2e"
        
        # Phase 1: Calculate all geometry
        self.setup_geometry()
        
        # Phase 2: Execute scenes
        self.scene_opening()
        self.scene_circumcenter()
        self.scene_incenter()
        self.scene_outro()
    
    def setup_geometry(self):
        """Calculate all coordinates precisely"""
        # Base triangle
        self.A = np.array([-2.5, 1.5, 0]) * 0.9 + UP * 1.5
        self.B = np.array([2.5, -0.5, 0]) * 0.9 + UP * 1.5
        self.C = np.array([-1.0, -2.5, 0]) * 0.9 + UP * 1.5
        
        # Side lengths
        self.a = np.linalg.norm(self.B - self.C)
        self.b = np.linalg.norm(self.C - self.A)
        self.c = np.linalg.norm(self.A - self.B)
        
        # Centers
        self.O = GeometryCalculator.circumcenter(self.A, self.B, self.C)
        self.I = GeometryCalculator.incenter(self.A, self.B, self.C)
        
        # Midpoints
        self.M_AB = (self.A + self.B) / 2
        self.M_BC = (self.B + self.C) / 2
        
        # Verify
        self.verify_geometry()
    
    def verify_geometry(self):
        """Verify all calculations"""
        epsilon = 1e-6
        
        # Circumcenter: equidistant from vertices
        r_A = np.linalg.norm(self.O - self.A)
        r_B = np.linalg.norm(self.O - self.B)
        r_C = np.linalg.norm(self.O - self.C)
        assert abs(r_A - r_B) < epsilon, f"Circumcenter error"
        assert abs(r_B - r_C) < epsilon, f"Circumcenter error"
        
        print("✓ Geometry verified")
    
    def scene_opening(self):
        """Opening hook"""
        # Author info
        self.author = Text(
            "上海初高中数学直通车 @emptyandcalm",
            font="Noto Sans CJK SC",
            font_size=20,
            color=GRAY_B
        ).move_to(UP * 7)
        self.play(FadeIn(self.author, shift=DOWN*0.2), run_time=0.3)
        
        # Hook
        hook = Text(
            "三角形有哪些神奇的中心?",
            font="Noto Sans CJK SC",
            font_size=40,
            color=GOLD
        ).move_to(UP * 6)
        self.play(Write(hook), run_time=0.8)
        
        # Triangle
        self.triangle = Polygon(self.A, self.B, self.C, 
                               color=WHITE, stroke_width=3)
        self.play(Create(self.triangle), run_time=1.0)
        self.wait(1.0)
        
        self.play(FadeOut(hook), run_time=0.5)
    
    def scene_circumcenter(self):
        """Show circumcenter"""
        # Title - CORRECT: Chinese in Text()
        title = Text(
            "外心 Circumcenter",
            font="Noto Sans CJK SC",
            font_size=36,
            color="#e74c3c"
        ).move_to(UP * 5.5)
        
        definition = Text(
            "三边垂直平分线的交点",
            font="Noto Sans CJK SC",
            font_size=24,
            color=GRAY_A
        ).move_to(UP * 4.8)
        
        self.play(Write(title), FadeIn(definition), run_time=0.8)
        
        # Perpendicular bisector of AB
        m_ab_dot = Dot(self.M_AB, color=GRAY_B, radius=0.06)
        
        # Calculate perpendicular direction
        dir_AB = self.B - self.A
        perp_AB = np.array([-dir_AB[1], dir_AB[0], 0])
        perp_AB_unit = perp_AB / np.linalg.norm(perp_AB)
        
        perp_line = DashedLine(
            self.M_AB - 2.5 * perp_AB_unit,
            self.M_AB + 2.5 * perp_AB_unit,
            color=GRAY_B,
            dash_length=0.1
        )
        
        self.play(FadeIn(m_ab_dot), Create(perp_line), run_time=1.0)
        
        # Perpendicular bisector of BC
        m_bc_dot = Dot(self.M_BC, color=GRAY_B, radius=0.06)
        
        dir_BC = self.C - self.B
        perp_BC = np.array([-dir_BC[1], dir_BC[0], 0])
        perp_BC_unit = perp_BC / np.linalg.norm(perp_BC)
        
        perp_line_2 = DashedLine(
            self.M_BC - 2.5 * perp_BC_unit,
            self.M_BC + 2.5 * perp_BC_unit,
            color=GRAY_B,
            dash_length=0.1
        )
        
        self.play(FadeIn(m_bc_dot), Create(perp_line_2), run_time=0.8)
        
        # Circumcenter
        o_dot = Dot(self.O, color="#e74c3c", radius=0.12)
        o_label = Text("O", font="Noto Sans CJK SC", 
                      font_size=24, color="#e74c3c").next_to(o_dot, RIGHT)
        
        self.play(FadeIn(o_dot, scale=0.5), run_time=0.5)
        self.play(Flash(o_dot, color="#e74c3c"), run_time=0.4)
        self.play(FadeIn(o_label), run_time=0.4)
        
        # Circumcircle
        radius = np.linalg.norm(self.O - self.A)
        circle = Circle(radius=radius, color="#e74c3c", 
                       stroke_width=2).move_to(self.O)
        self.play(Create(circle), run_time=1.5)
        
        # Property text
        prop = Text(
            "到三顶点距离相等",
            font="Noto Sans CJK SC",
            font_size=22,
            color=GRAY_A
        ).move_to(DOWN * 5)
        self.play(FadeIn(prop), run_time=0.5)
        self.wait(2.0)
        
        # Cleanup
        self.play(
            FadeOut(title), FadeOut(definition),
            FadeOut(perp_line), FadeOut(perp_line_2),
            FadeOut(m_ab_dot), FadeOut(m_bc_dot),
            FadeOut(circle), FadeOut(o_label), FadeOut(prop),
            run_time=0.6
        )
        
        # Keep small dot
        self.o_small = Dot(self.O, color="#e74c3c", 
                          radius=0.05, fill_opacity=0.5)
        self.play(Transform(o_dot, self.o_small), run_time=0.3)
        self.remove(o_dot)
        self.add(self.o_small)
    
    def scene_incenter(self):
        """Show incenter"""
        title = Text(
            "内心 Incenter",
            font="Noto Sans CJK SC",
            font_size=36,
            color="#3498db"
        ).move_to(UP * 5.5)
        
        definition = Text(
            "三条角平分线的交点",
            font="Noto Sans CJK SC",
            font_size=24,
            color=GRAY_A
        ).move_to(UP * 4.8)
        
        self.play(Write(title), FadeIn(definition), run_time=0.8)
        
        # Angle bisector from A
        v1 = (self.B - self.A) / np.linalg.norm(self.B - self.A)
        v2 = (self.C - self.A) / np.linalg.norm(self.C - self.A)
        bisector_dir = (v1 + v2) / np.linalg.norm(v1 + v2)
        
        # Calculate intersection with BC using angle bisector theorem
        t = self.c / (self.b + self.c)
        D = self.B + t * (self.C - self.B)
        
        bisector = DashedLine(self.A, D, color=GRAY_B, dash_length=0.1)
        self.play(Create(bisector), run_time=1.0)
        
        # Incenter
        i_dot = Dot(self.I, color="#3498db", radius=0.12)
        i_label = Text("I", font="Noto Sans CJK SC",
                      font_size=24, color="#3498db").next_to(i_dot, RIGHT)
        
        self.play(FadeIn(i_dot, scale=0.5), run_time=0.5)
        self.play(Flash(i_dot, color="#3498db"), run_time=0.4)
        self.play(FadeIn(i_label), run_time=0.4)
        
        # Incircle
        # Calculate inradius: distance from incenter to any side
        vec_BC = self.C - self.B
        vec_BI = self.I - self.B
        cross = np.abs(np.cross(vec_BI[:2], vec_BC[:2]))
        inradius = cross / np.linalg.norm(vec_BC)
        
        incircle = Circle(radius=inradius, color="#3498db",
                         stroke_width=2).move_to(self.I)
        self.play(Create(incircle), run_time=1.5)
        
        prop = Text(
            "到三边距离相等",
            font="Noto Sans CJK SC",
            font_size=22,
            color=GRAY_A
        ).move_to(DOWN * 5)
        self.play(FadeIn(prop), run_time=0.5)
        self.wait(2.0)
        
        # Cleanup
        self.play(
            FadeOut(title), FadeOut(definition),
            FadeOut(bisector), FadeOut(incircle),
            FadeOut(i_label), FadeOut(prop),
            run_time=0.6
        )
        
        self.i_small = Dot(self.I, color="#3498db",
                          radius=0.05, fill_opacity=0.5)
        self.play(Transform(i_dot, self.i_small), run_time=0.3)
        self.remove(i_dot)
        self.add(self.i_small)
    
    def scene_outro(self):
        """Closing call to action"""
        # Enlarge author
        author_large = Text(
            "上海初高中数学直通车\n@emptyandcalm",
            font="Noto Sans CJK SC",
            font_size=36
        ).move_to(UP * 1)
        
        self.play(Transform(self.author, author_large), run_time=0.8)
        
        # CTA
        cta = Text(
            "关注我,学更多数学技巧!",
            font="Noto Sans CJK SC",
            font_size=32,
            color=YELLOW
        ).move_to(DOWN * 1)
        
        self.play(FadeIn(cta, shift=UP*0.3), run_time=0.6)
        self.wait(2.0)
