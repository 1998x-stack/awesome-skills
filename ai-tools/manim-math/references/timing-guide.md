# Animation Timing Guide

Professional timing standards for educational math animations.

## Core Principles

1. **Slow for complexity** - Difficult concepts need more time
2. **Fast for simplicity** - Don't bore with obvious steps
3. **Rhythm and breath** - Mix action with pauses
4. **Student-paced** - Allow time to process

## Standard Timings

### Object Creation

| Type | Duration | Example |
|------|----------|---------|
| Point/dot | 0.3-0.5s | `FadeIn(dot, scale=0.5)` |
| Simple line | 0.5-0.8s | `Create(line)` |
| Triangle | 1.0-1.2s | `Create(triangle)` |
| Circle | 0.8-1.0s | `Create(circle)` |
| Complex polygon | 1.2-1.5s | `Create(hexagon)` |
| Arc/sector | 0.8-1.0s | `Create(arc)` |

### Text and Formulas

| Type | Duration | Example |
|------|----------|---------|
| Short text (1-5 chars) | 0.4-0.6s | `Write(label)` |
| Medium text (6-15 chars) | 0.6-0.8s | `Write(title)` |
| Long text (16+ chars) | 0.8-1.2s | `Write(paragraph)` |
| Simple formula | 0.6-0.8s | `Write(MathTex("a^2"))` |
| Complex formula | 0.8-1.2s | `Write(MathTex("\\frac{...}"))` |
| Multi-line formula | 1.0-1.5s | `Write(equation_system)` |

### Transformations

| Type | Duration | Example |
|------|----------|---------|
| Simple movement | 0.6-0.8s | `obj.animate.shift(RIGHT)` |
| Rotation | 0.8-1.0s | `Rotate(obj, PI/2)` |
| Scaling | 0.6-0.8s | `obj.animate.scale(0.5)` |
| Transform | 0.8-1.2s | `Transform(a, b)` |
| Color change | 0.4-0.6s | `obj.animate.set_color(RED)` |
| Fade in/out | 0.3-0.5s | `FadeIn(obj)` |

### Pauses (Wait)

| Purpose | Duration | When to Use |
|---------|----------|-------------|
| Micro pause | 0.2-0.3s | Between rapid actions |
| Transition | 0.5-0.8s | Scene changes |
| Observation | 1.0-1.5s | Let student see result |
| **Understanding** | **2.0-3.0s** | **After key concepts** |
| Dramatic pause | 1.5-2.0s | Before reveal |
| Final pause | 2.0-3.0s | Before outro |

## Pacing Patterns

### Pattern 1: Quick Introduction

```python
# Fast-paced for simple setup (3-4 seconds total)
self.play(Create(triangle), run_time=0.8)
self.play(Write(label_A), Write(label_B), Write(label_C), run_time=0.6)
self.wait(0.5)
```

### Pattern 2: Step-by-Step Construction

```python
# Methodical pacing for learning (8-10 seconds per step)
# Step 1
self.play(Write(step_title), run_time=0.6)
self.wait(0.3)
self.play(Create(construction_line), run_time=1.2)
self.wait(0.5)
self.play(FadeIn(point_dot, scale=0.5), run_time=0.4)
self.wait(2.0)  # Understanding pause

# Step 2
self.play(FadeOut(step_title), run_time=0.3)
# ... next step
```

### Pattern 3: Proof Sequence

```python
# Deliberate pacing for reasoning (12-15 seconds per step)
# Show premise
self.play(Write(premise), run_time=1.0)
self.wait(2.5)  # Long pause to read and understand

# Show logical step
self.play(
    TransformMatchingTex(premise, conclusion),
    run_time=1.5
)
self.wait(2.0)  # Understand transformation

# Emphasize result
self.play(Circumscribe(key_part, color=YELLOW), run_time=1.2)
self.wait(3.0)  # Critical understanding pause
```

### Pattern 4: Reveal Sequence

```python
# Build suspense then reveal (5-6 seconds)
# Build up
self.play(Create(auxiliary_lines), run_time=1.2)
self.wait(0.8)

# Dramatic pause
self.wait(1.5)

# Reveal
self.play(
    FadeIn(special_point, scale=2),
    Flash(special_point, color=YELLOW),
    run_time=1.0
)
self.wait(2.0)
```

## TikTok-Specific Guidelines

### Total Duration

- **Ideal:** 45-60 seconds (high retention)
- **Acceptable:** 60-90 seconds (good content)
- **Maximum:** 90-120 seconds (must be exceptional)

### Section Breakdown

```
┌─────────────────────────────────────┐
│ Opening Hook        │ 3-5s  │  8%   │ ← Grab attention
├─────────────────────────────────────┤
│ Introduction        │ 8-12s │ 18%   │ ← Set context
├─────────────────────────────────────┤
│ Main Content        │ 30-40s│ 60%   │ ← Core teaching
│ (2-4 key concepts)  │       │       │
├─────────────────────────────────────┤
│ Summary/Conclusion  │ 4-6s  │  9%   │ ← Wrap up
├─────────────────────────────────────┤
│ Outro/CTA           │ 3-5s  │  5%   │ ← Call to action
└─────────────────────────────────────┘
```

### Engagement Hooks

**First 3 seconds are critical!**

```python
# ❌ BORING - Slow start
self.play(FadeIn(title), run_time=2.0)
self.wait(1.0)
self.play(Write(long_explanation), run_time=3.0)

# ✅ ENGAGING - Immediate visual
self.play(Create(striking_figure), run_time=0.8)  # Instant visual
self.play(Write(hook_question), run_time=0.6)    # Quick question
self.wait(0.3)
self.play(Flash(mystery_point), run_time=0.4)    # Intrigue
```

## Rhythm and Flow

### Good Rhythm Example

```python
def good_rhythm_scene(self):
    # Fast action
    self.play(Create(line), run_time=0.6)
    
    # Brief pause
    self.wait(0.3)
    
    # Medium action
    self.play(Write(label), run_time=0.8)
    
    # Understanding pause
    self.wait(1.5)
    
    # Fast action
    self.play(FadeIn(dot), run_time=0.4)
    
    # Dramatic pause
    self.wait(2.5)
```

**Analysis:** Varies between 0.3s and 2.5s - keeps attention

### Bad Rhythm Example

```python
def bad_rhythm_scene(self):
    # All slow
    self.play(Create(line), run_time=2.0)
    self.wait(2.0)
    self.play(Write(label), run_time=2.0)
    self.wait(2.0)
```

**Problem:** Monotonous, loses attention

## Rate Functions

Use rate functions for natural motion:

```python
# Smooth acceleration and deceleration (default, best for most cases)
self.play(obj.animate.move_to(target), rate_func=smooth)

# Linear motion (mechanical, use sparingly)
self.play(obj.animate.move_to(target), rate_func=linear)

# Rush into (accelerate into position)
self.play(obj.animate.move_to(target), rate_func=rush_into)

# Rush from (decelerate from position)
self.play(obj.animate.move_to(target), rate_func=rush_from)

# There and back (oscillate)
self.play(obj.animate.move_to(target), rate_func=there_and_back)

# Wiggle (emphasis)
self.play(obj.animate.scale(1.1), rate_func=there_and_back, run_time=0.6)
```

## Special Timing Considerations

### For Different Age Groups

**Elementary (Grade 1-6):**
- 20% longer pauses
- Simpler vocabulary needs slower reading time
- More repetition of key points

```python
# Elementary adjustment
PAUSE_MULTIPLIER = 1.2
self.wait(2.0 * PAUSE_MULTIPLIER)  # 2.4s pause
```

**Middle School (Grade 7-9):**
- Standard timings (as listed above)
- Balance between pace and comprehension

**High School (Grade 10-12):**
- 10% faster allowed for familiar concepts
- But keep 2-3s pauses for new ideas

```python
# High school adjustment
PAUSE_MULTIPLIER = 0.9
self.wait(2.0 * PAUSE_MULTIPLIER)  # 1.8s pause for review
self.wait(2.5)  # Full 2.5s for new concepts
```

### For Different Complexity

**Simple concept (e.g., midpoint):**
- Fast demo: 0.8s create + 0.5s pause
- Label: 0.4s
- Total: ~2 seconds

**Medium concept (e.g., angle bisector):**
- Construction: 1.2s
- Verification: 0.8s
- Explanation: 1.0s
- Pause: 2.0s
- Total: ~5 seconds

**Complex concept (e.g., orthocenter):**
- Setup: 1.5s
- First altitude: 1.2s + 0.8s pause
- Second altitude: 1.0s + 0.5s pause
- Intersection: 1.0s
- Property explanation: 1.5s
- Understanding pause: 3.0s
- Total: ~10-12 seconds

## Timing Checklist

Before rendering, verify:

- [ ] Opening hook within 3-5 seconds
- [ ] No pause longer than 3 seconds (except dramatic moments)
- [ ] Key concepts have 2-3 second pauses
- [ ] Simple actions are 0.5-1.0 seconds
- [ ] Total duration within target range
- [ ] Rhythm varies (not all same speed)
- [ ] Rate functions used appropriately
- [ ] Adjusted for target age group

## Testing Timing

```python
# Add timing debug output
import time

class TimedScene(Scene):
    def construct(self):
        self.scene_start = time.time()
        self.scene_opening()
        print(f"Opening: {time.time() - self.scene_start:.1f}s")
        
        scene_2_start = time.time()
        self.scene_main_content()
        print(f"Main: {time.time() - scene_2_start:.1f}s")
        
        # ... etc
```

## Professional Polish

**Final timing review:**

1. **Watch without audio** - Are visuals self-explanatory?
2. **Watch at 1.5x speed** - Does it still make sense?
3. **Watch with target student** - Do they understand?
4. **Check analytics** - Where do viewers drop off?

**Optimization:**
- If >50% drop before 15s → Speed up opening
- If drop during middle → Reduce explanation length
- If drop at end → Shorten outro

**Golden rule:** Better to be slightly too fast (replayable) than too slow (boring).
