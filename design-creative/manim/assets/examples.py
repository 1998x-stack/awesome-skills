#!/usr/bin/env python3
"""
Manim 示例模板脚本
包含常用动画模式的示例

渲染命令:
  manim -pql examples.py EquationDemo      # 公式动画
  manim -pql examples.py GraphDemo         # 函数图像
  manim -pql examples.py ValueTrackerDemo  # 动态追踪
  manim -pql examples.py ThreeDDemo        # 3D 场景
"""

from manim import *
import numpy as np


class EquationDemo(Scene):
    """公式推导动画示例"""
    
    def construct(self):
        # 标题
        title = Text("二项式定理", font_size=48)
        self.play(Write(title))
        self.wait()
        self.play(title.animate.to_edge(UP))
        
        # 公式推导
        step1 = MathTex(r"(a+b)^2")
        step2 = MathTex(r"(a+b)(a+b)")
        step3 = MathTex(r"a^2 + ab + ba + b^2")
        step4 = MathTex(r"a^2 + 2ab + b^2")
        
        # 显示第一步
        self.play(Write(step1))
        self.wait()
        
        # 逐步变换
        for next_step in [step2, step3, step4]:
            next_step.move_to(step1)
            self.play(TransformMatchingTex(step1, next_step))
            self.wait()
            step1 = next_step
        
        # 高亮结果
        box = SurroundingRectangle(step4, color=YELLOW, buff=0.2)
        self.play(Create(box))
        self.wait()


class GraphDemo(Scene):
    """函数图像动画示例"""
    
    def construct(self):
        # 创建坐标轴
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 4, 1],
            x_length=8,
            y_length=5,
            axis_config={"include_numbers": True}
        )
        labels = axes.get_axis_labels(x_label="x", y_label="y")
        
        self.play(Create(axes), Write(labels))
        
        # 绘制 y = x^2
        graph1 = axes.plot(lambda x: x**2, color=BLUE)
        label1 = axes.get_graph_label(graph1, r"y = x^2", x_val=1.5)
        
        self.play(Create(graph1), Write(label1))
        self.wait()
        
        # 变换为 y = x^2 - 1 (向下平移)
        graph2 = axes.plot(lambda x: x**2 - 1, color=RED)
        label2 = axes.get_graph_label(graph2, r"y = x^2 - 1", x_val=1.5)
        
        self.play(
            Transform(graph1, graph2),
            Transform(label1, label2)
        )
        self.wait()


class ValueTrackerDemo(Scene):
    """ValueTracker 动态动画示例"""
    
    def construct(self):
        # 坐标轴
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 25, 5])
        axes.add_coordinates()
        
        # 函数 f(x) = x^2
        graph = axes.plot(lambda x: x**2, color=BLUE)
        
        # 追踪器
        t = ValueTracker(0)
        
        # 动态点
        dot = always_redraw(
            lambda: Dot(
                axes.c2p(t.get_value(), t.get_value()**2),
                color=RED
            )
        )
        
        # 动态标签
        label = always_redraw(
            lambda: MathTex(
                f"({t.get_value():.1f}, {t.get_value()**2:.1f})"
            ).next_to(dot, UR)
        )
        
        # 切线
        tangent = always_redraw(
            lambda: axes.get_secant_slope_group(
                x=t.get_value(),
                graph=graph,
                dx=0.01,
                secant_line_length=3,
                secant_line_color=YELLOW
            )
        )
        
        self.add(axes, graph, dot, label, tangent)
        
        # 动画
        self.play(t.animate.set_value(4), run_time=4)
        self.wait()


class ThreeDDemo(ThreeDScene):
    """3D 场景示例"""
    
    def construct(self):
        # 设置相机
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        
        # 3D 坐标轴
        axes = ThreeDAxes(
            x_range=[-3, 3],
            y_range=[-3, 3],
            z_range=[-2, 2]
        )
        
        # 3D 曲面 z = sin(x) * cos(y)
        surface = Surface(
            lambda u, v: axes.c2p(u, v, np.sin(u) * np.cos(v)),
            u_range=[-PI, PI],
            v_range=[-PI, PI],
            resolution=(30, 30),
            fill_opacity=0.7
        )
        surface.set_fill_by_checkerboard(BLUE, GREEN, opacity=0.5)
        
        self.add(axes)
        self.play(Create(surface), run_time=2)
        
        # 相机旋转
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(5)
        self.stop_ambient_camera_rotation()


class MatrixDemo(Scene):
    """矩阵动画示例"""
    
    def construct(self):
        # 矩阵
        matrix = Matrix([
            [1, 2],
            [3, 4]
        ], left_bracket="(", right_bracket=")")
        
        self.play(Write(matrix))
        self.wait()
        
        # 行列式
        det_eq = MathTex(r"\det(A) = 1 \cdot 4 - 2 \cdot 3 = -2")
        det_eq.next_to(matrix, DOWN, buff=1)
        
        self.play(Write(det_eq))
        self.wait()


class ComplexNumberDemo(Scene):
    """复数平面动画示例"""
    
    def construct(self):
        # 复平面
        plane = ComplexPlane(
            x_range=[-4, 4],
            y_range=[-3, 3]
        ).add_coordinates()
        
        self.play(Create(plane))
        
        # 复数 z = 2 + i
        z = complex(2, 1)
        dot = Dot(plane.n2p(z), color=RED)
        label = MathTex("z = 2 + i").next_to(dot, UR)
        
        # 从原点到 z 的向量
        arrow = Arrow(plane.n2p(0), plane.n2p(z), color=YELLOW, buff=0)
        
        self.play(GrowArrow(arrow), FadeIn(dot), Write(label))
        self.wait()
        
        # z^2 的动画
        z_squared = z ** 2
        dot2 = Dot(plane.n2p(z_squared), color=BLUE)
        arrow2 = Arrow(plane.n2p(0), plane.n2p(z_squared), color=GREEN, buff=0)
        label2 = MathTex("z^2 = 3 + 4i").next_to(dot2, UR)
        
        self.play(
            Transform(arrow.copy(), arrow2),
            FadeIn(dot2),
            Write(label2)
        )
        self.wait()


if __name__ == "__main__":
    print("运行命令示例:")
    print("  manim -pql examples.py EquationDemo")
    print("  manim -pql examples.py GraphDemo")
    print("  manim -pql examples.py ValueTrackerDemo")
    print("  manim -pql examples.py ThreeDDemo")
    print("  manim -pql examples.py MatrixDemo")
    print("  manim -pql examples.py ComplexNumberDemo")
