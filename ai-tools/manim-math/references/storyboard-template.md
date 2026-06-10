# Storyboard Template

Template for planning Manim math animations with precise scene breakdown.

## Template Structure

```markdown
# [Animation Title] - Storyboard

## Metadata
- **Target Duration:** XX seconds
- **Total Scenes:** X
- **Difficulty Level:** Elementary/Middle/High School
- **Key Concepts:** [List main ideas]

## Color Scheme
```python
COLOR_PRIMARY = "#3498db"      # Main concept color
COLOR_SECONDARY = "#e74c3c"    # Secondary elements
COLOR_HIGHLIGHT = YELLOW       # Important highlights
COLOR_AUXILIARY = GRAY_B       # Construction lines
BACKGROUND = "#1a1a2e"         # Dark background
```

## Geometry Pre-calculations

| Element | Formula | Variable Name | Verification |
|---------|---------|---------------|--------------|
| Midpoint M | (A+B)/2 | self.M_AB | len(AM) = len(MB) |
| Circumcenter O | Three perp bisectors | self.O | dist(OA)=dist(OB)=dist(OC) |
| Altitude foot | Perpendicular projection | self.H_A | AH ⊥ BC |

---

## Scene 1: Opening Hook
**Duration:** 3-4 seconds  
**Purpose:** Grab attention, introduce problem

### Elements
1. Author branding (top)
2. Attention-grabbing question (large text)
3. Visual preview of problem

### Animation Sequence

| Time | Action | Code Pattern | Cleanup |
|------|--------|-------------|---------|
| 0.0s | Author info fade in | `FadeIn(author, shift=DOWN*0.2)` | Keep |
| 0.3s | Hook text write | `Write(hook_text, run_time=0.8)` | Remove at 3.0s |
| 1.1s | Main figure create | `Create(triangle, run_time=1.0)` | Keep |
| 2.1s | Brief pause | `Wait(1.0)` | - |
| 3.0s | Clean hook text | `FadeOut(hook_text)` | - |

### Layout
```
┌─────────────────────────┐ y=+8
│  Author: 上海初高中...    │ y=+7
├─────────────────────────┤
│                         │
│  Hook Question (大字)    │ y=+6
│                         │
├─────────────────────────┤ y=+5
│                         │
│   [Preview Figure]      │ y=+2
│                         │
└─────────────────────────┘
```

---

## Scene 2: [Concept Introduction]
**Duration:** 5-6 seconds  
**Purpose:** Explain first key concept

### Elements
1. Title text (concept name)
2. Definition/explanation
3. Initial geometric construction

### Animation Sequence

| Time | Action | Code Pattern | Notes |
|------|--------|-------------|-------|
| 3.0s | Title slide in | `Write(title, run_time=0.6)` | 中文用Text() |
| 3.6s | Definition appear | `FadeIn(definition, shift=UP*0.3)` | |
| 4.2s | First construction line | `Create(line_1, run_time=0.8)` | 辅助线用虚线 |
| 5.0s | Mark special points | `FadeIn(dot_group, lag_ratio=0.2)` | |
| 6.0s | Explanation text | `Write(explanation)` | 底部文字区 |
| 8.0s | Pause for understanding | `Wait(2.0)` | **关键停顿** |

### Geometry Calculations Needed
```python
# Example for altitude
foot_D = GeometryCalculator.perpendicular_foot(A, B, C)
altitude = DashedLine(A, foot_D, color=COLOR_AUXILIARY)

# Verify perpendicularity
vec_AD = foot_D - A
vec_BC = C - B
assert abs(np.dot(vec_AD[:2], vec_BC[:2])) < 1e-6
```

### Cleanup Strategy
- **Keep:** Main figure, important points
- **Remove:** Title, definition, temporary construction lines
- **Fade:** Reduce opacity of auxiliary elements

---

## Scene 3: [Construction/Proof Step]
**Duration:** 6-8 seconds  
**Purpose:** Show geometric construction or proof step

### Elements
1. Step indicator (步骤 1/3)
2. Construction animation
3. Angle/length markings
4. Reasoning text

### Critical Timing
- **Construction:** 1.5-2.0s (让学生看清)
- **Highlighting:** 0.5-0.8s (突出重点)
- **Explanation:** 1.0-1.5s (文字说明)
- **Pause:** 2.0-3.0s (理解消化)

### Example: Drawing Angle Bisector
```python
def scene_3_angle_bisector(self):
    # Step indicator
    step_text = Text("步骤 1: 作角平分线", 
                     font="Noto Sans CJK SC", 
                     font_size=28).to_edge(UP)
    self.play(FadeIn(step_text))
    
    # Calculate bisector endpoint
    v1 = (self.B - self.A) / np.linalg.norm(self.B - self.A)
    v2 = (self.C - self.A) / np.linalg.norm(self.C - self.A)
    bisector_dir = (v1 + v2) / np.linalg.norm(v1 + v2)
    D = self.A + 3 * bisector_dir
    
    # Animate bisector
    bisector = DashedLine(self.A, D, color=COLOR_PRIMARY)
    self.play(Create(bisector), run_time=1.5)
    
    # Mark equal angles
    angle1 = Angle.from_three_points(self.B, self.A, D, radius=0.4)
    angle2 = Angle.from_three_points(D, self.A, self.C, radius=0.4)
    angle1.set_color(YELLOW)
    angle2.set_color(YELLOW)
    
    self.play(Create(angle1), Create(angle2), run_time=0.8)
    
    # Explanation
    explanation = Text("∠BAD = ∠CAD", 
                      font="Noto Sans CJK SC",
                      font_size=24).move_to(DOWN*4)
    self.play(Write(explanation), run_time=0.8)
    
    self.wait(2.0)  # Understanding pause
```

---

## Scene N-1: Summary/Conclusion
**Duration:** 4-5 seconds  
**Purpose:** Recap key points

### Elements
1. Final figure (all constructions)
2. Key property statements
3. Formula/theorem box

### Layout Example
```
┌─────────────────────────┐
│   [完整图形]             │ y=+3
├─────────────────────────┤
│  关键性质:               │ y=+0
│  • 性质1                 │
│  • 性质2                 │
│  • 性质3                 │
├─────────────────────────┤
│  ┌───────────────────┐  │ y=-3
│  │ 定理/公式         │  │
│  └───────────────────┘  │
└─────────────────────────┘
```

---

## Scene N: Outro (Call to Action)
**Duration:** 3-4 seconds  
**Purpose:** Encourage engagement

### Elements
1. Author info (enlarged)
2. "关注我,学更多数学技巧!"
3. Animated decorations

### Animation Pattern
```python
def scene_outro(self):
    # Enlarge author info
    author_large = Text(
        "上海初高中数学直通车\n@emptyandcalm",
        font="Noto Sans CJK SC",
        font_size=36
    ).move_to(UP*1)
    
    self.play(Transform(self.author_info, author_large))
    
    # Call to action
    cta = Text(
        "关注我,学更多数学技巧!",
        font="Noto Sans CJK SC",
        font_size=32,
        color=YELLOW
    ).move_to(DOWN*1)
    
    self.play(FadeIn(cta, shift=UP*0.3, scale=1.1))
    
    # Decorative elements
    shapes = VGroup(*[
        RegularPolygon(n=3, color=GOLD).scale(0.3)
        .move_to(cta.get_center() + 2*np.array([cos(i*PI/3), sin(i*PI/3), 0]))
        for i in range(6)
    ])
    
    self.play(*[FadeIn(s, scale=0.5) for s in shapes])
    self.play(Rotate(shapes, PI, run_time=1.5))
    self.wait(1)
```

---

## Element Lifecycle Tracking

| Element | Created In | Removed In | Notes |
|---------|------------|------------|-------|
| author_info | Scene 1 | Scene N | Present throughout |
| triangle | Scene 1 | Scene N | Main figure |
| hook_text | Scene 1 | Scene 1 | Opening only |
| aux_line_1 | Scene 2 | Scene 3 | Temporary |
| angle_mark | Scene 3 | Scene N-1 | Keep until summary |

---

## Timing Budget

| Category | Time | Percentage |
|----------|------|------------|
| Opening | 3-4s | 5% |
| Concept intro | 10-15s | 20% |
| Construction steps | 30-40s | 55% |
| Summary | 4-5s | 8% |
| Outro | 3-4s | 5% |
| **Total** | **~60s** | **100%** |

**Target:** 45-90 seconds for TikTok optimization

---

## Checklist Before Implementation

- [ ] All geometry calculations documented
- [ ] Verification conditions specified
- [ ] Scene transitions planned
- [ ] Element lifecycle tracked
- [ ] Timing within guidelines
- [ ] Text uses correct methods (Text vs MathTex)
- [ ] Colors defined and consistent
- [ ] Cleanup strategy clear

---

## Notes Section

**特殊注意事项:**
- 角度大于180°时,需检查other_angle参数
- 所有中文使用Text(),数学公式使用MathTex()
- 关键步骤留出2-3秒理解时间
- 虚线使用DashedLine或DashedVMobject

**调试策略:**
- 使用-ql快速预览
- 验证几何计算正确性
- 检查元素是否超出边界
- 测试不同场景切换效果
```

## Using This Template

1. **Copy template structure** to new file
2. **Fill in metadata** (duration, difficulty, concepts)
3. **Plan geometry** calculations first
4. **Design each scene** with timing
5. **Track element lifecycle** throughout
6. **Verify checklist** before coding
