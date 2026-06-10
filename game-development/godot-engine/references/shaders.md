# Godot Shaders

## Table of Contents
1. [Shader Types](#shader-types)
2. [Shader Language Basics](#shader-language-basics)
3. [2D Shaders](#2d-shaders)
4. [3D Shaders](#3d-shaders)
5. [Particle Shaders](#particle-shaders)
6. [Visual Shaders](#visual-shaders)
7. [Common Effects](#common-effects)

---

## Shader Types

| Type | Keyword | Use Case |
|------|---------|----------|
| Spatial | `shader_type spatial;` | 3D objects |
| Canvas Item | `shader_type canvas_item;` | 2D sprites, UI |
| Particles | `shader_type particles;` | GPU particles |
| Sky | `shader_type sky;` | Sky rendering |
| Fog | `shader_type fog;` | Volumetric fog |

---

## Shader Language Basics

Godot uses its own shading language, similar to GLSL but with Godot-specific features.

### Data Types
```glsl
// Scalars
bool, int, uint, float

// Vectors
vec2, vec3, vec4       // float vectors
ivec2, ivec3, ivec4    // int vectors
bvec2, bvec3, bvec4    // bool vectors
uvec2, uvec3, uvec4    // unsigned int vectors

// Matrices
mat2, mat3, mat4

// Samplers
sampler2D, sampler3D, samplerCube
```

### Uniforms (Exposed Parameters)
```glsl
shader_type canvas_item;

uniform float speed : hint_range(0.0, 10.0, 0.1) = 1.0;
uniform vec4 tint_color : source_color = vec4(1.0);
uniform sampler2D noise_texture : repeat_enable;
uniform float amplitude = 0.1;

// Groups (Godot 4)
group_uniforms MyGroup;
uniform float param_a = 1.0;
uniform float param_b = 2.0;
group_uniforms;
```

### Uniform Hints
```glsl
hint_range(min, max, step)    // Slider in inspector
source_color                   // Color picker
hint_normal                    // Normal map
hint_default_white             // Default white texture
hint_default_black             // Default black texture
hint_anisotropy                // Anisotropy texture
repeat_enable                  // Texture repeats
repeat_disable                 // No repeat
filter_nearest                 // Pixel-perfect filtering
filter_linear                  // Smooth filtering
```

### Built-in Variables (Canvas Item)
```glsl
// Vertex function
VERTEX     // vec2 - vertex position
UV         // vec2 - texture coordinates
COLOR      // vec4 - vertex color
POINT_SIZE // float

// Fragment function
UV          // vec2
COLOR       // vec4 - output color
TEXTURE     // sampler2D - main texture
SCREEN_UV   // vec2 - screen-space UVs
SCREEN_TEXTURE // removed in Godot 4! Use hint_screen_texture
TIME        // float - seconds since start

// Godot 4: Screen texture access
uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;
```

### Built-in Variables (Spatial)
```glsl
// Vertex function
VERTEX       // vec3
NORMAL       // vec3
UV           // vec2
UV2          // vec2
COLOR        // vec4
MODEL_MATRIX // mat4
VIEW_MATRIX  // mat4
PROJECTION_MATRIX // mat4

// Fragment function
ALBEDO       // vec3 - base color
METALLIC     // float
ROUGHNESS    // float
SPECULAR     // float
EMISSION     // vec3
NORMAL_MAP   // vec3
ALPHA        // float
AO           // float - ambient occlusion
```

---

## 2D Shaders

### Basic Sprite Shader
```glsl
shader_type canvas_item;

uniform vec4 modulate_color : source_color = vec4(1.0);
uniform float flash_amount : hint_range(0.0, 1.0) = 0.0;
uniform vec4 flash_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);

void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    // Mix with flash color (for hit flash effect)
    tex.rgb = mix(tex.rgb, flash_color.rgb, flash_amount);
    COLOR = tex * modulate_color;
}
```

### Dissolve Effect
```glsl
shader_type canvas_item;

uniform float dissolve_amount : hint_range(0.0, 1.0) = 0.0;
uniform sampler2D noise_texture;
uniform vec4 edge_color : source_color = vec4(1.0, 0.5, 0.0, 1.0);
uniform float edge_width : hint_range(0.0, 0.2) = 0.05;

void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    float noise = texture(noise_texture, UV).r;

    if (noise < dissolve_amount) {
        discard;
    }

    // Glowing edge
    float edge = smoothstep(dissolve_amount, dissolve_amount + edge_width, noise);
    tex.rgb = mix(edge_color.rgb, tex.rgb, edge);

    COLOR = tex;
}
```

### Outline Shader
```glsl
shader_type canvas_item;

uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float outline_width : hint_range(0.0, 10.0, 1.0) = 1.0;

void fragment() {
    vec2 size = TEXTURE_PIXEL_SIZE * outline_width;
    float alpha = texture(TEXTURE, UV).a;

    // Sample neighbors
    alpha = max(alpha, texture(TEXTURE, UV + vec2(size.x, 0.0)).a);
    alpha = max(alpha, texture(TEXTURE, UV + vec2(-size.x, 0.0)).a);
    alpha = max(alpha, texture(TEXTURE, UV + vec2(0.0, size.y)).a);
    alpha = max(alpha, texture(TEXTURE, UV + vec2(0.0, -size.y)).a);

    vec4 tex = texture(TEXTURE, UV);
    // Where original is transparent but neighbor exists, draw outline
    vec4 result = mix(vec4(outline_color.rgb, alpha), tex, tex.a);
    COLOR = result;
}
```

### Wave/Wobble Effect
```glsl
shader_type canvas_item;

uniform float wave_speed : hint_range(0.0, 10.0) = 2.0;
uniform float wave_amplitude : hint_range(0.0, 0.1) = 0.02;
uniform float wave_frequency : hint_range(0.0, 20.0) = 10.0;

void vertex() {
    VERTEX.x += sin(VERTEX.y * wave_frequency + TIME * wave_speed) * wave_amplitude * 100.0;
}
```

---

## 3D Shaders

### Basic PBR
```glsl
shader_type spatial;

uniform vec4 albedo_color : source_color = vec4(1.0);
uniform sampler2D albedo_texture : source_color;
uniform float metallic : hint_range(0.0, 1.0) = 0.0;
uniform float roughness : hint_range(0.0, 1.0) = 0.5;

void fragment() {
    vec4 tex = texture(albedo_texture, UV);
    ALBEDO = tex.rgb * albedo_color.rgb;
    METALLIC = metallic;
    ROUGHNESS = roughness;
    ALPHA = tex.a * albedo_color.a;
}
```

### Fresnel / Rim Lighting
```glsl
shader_type spatial;

uniform vec4 rim_color : source_color = vec4(0.0, 0.5, 1.0, 1.0);
uniform float rim_power : hint_range(0.1, 8.0) = 3.0;

void fragment() {
    float fresnel = pow(1.0 - dot(NORMAL, VIEW), rim_power);
    EMISSION = rim_color.rgb * fresnel;
}
```

### Triplanar Mapping
```glsl
shader_type spatial;

uniform sampler2D albedo_texture : source_color, repeat_enable;
uniform float texture_scale = 1.0;

void fragment() {
    vec3 weights = abs(NORMAL);
    weights = pow(weights, vec3(4.0));
    weights /= dot(weights, vec3(1.0));

    vec3 pos = VERTEX * texture_scale;
    vec3 color_x = texture(albedo_texture, pos.yz).rgb;
    vec3 color_y = texture(albedo_texture, pos.xz).rgb;
    vec3 color_z = texture(albedo_texture, pos.xy).rgb;

    ALBEDO = color_x * weights.x + color_y * weights.y + color_z * weights.z;
}
```

---

## Particle Shaders

```glsl
shader_type particles;

uniform float spread : hint_range(0.0, 3.14) = 1.0;
uniform float initial_speed : hint_range(0.0, 100.0) = 10.0;
uniform vec3 gravity = vec3(0.0, -9.8, 0.0);

void start() {
    float angle = hash(INDEX + 1.0) * spread - spread / 2.0;
    VELOCITY = vec3(sin(angle), cos(angle), 0.0) * initial_speed;
    TRANSFORM[3].xyz = EMISSION_TRANSFORM[3].xyz;
    COLOR = vec4(1.0, 0.5, 0.0, 1.0);
    CUSTOM.x = 0.0; // lifetime progress
}

void process() {
    VELOCITY += gravity * DELTA;
    CUSTOM.x += DELTA / LIFETIME;
    COLOR.a = 1.0 - CUSTOM.x; // Fade out
}
```

---

## Visual Shaders

For non-coders, Godot provides a node-based visual shader editor. Key nodes:

- **Input nodes** — UV, TIME, VERTEX, NORMAL, etc.
- **Math nodes** — Add, Multiply, Sin, Lerp, etc.
- **Texture nodes** — Sample textures
- **Output nodes** — Set ALBEDO, EMISSION, ALPHA, etc.

Visual shaders produce the same GLSL as text shaders — performance is identical.

---

## Common Effects

### Screen-Space Shaders (Post-Processing)
In Godot 4, attach a shader to a `ColorRect` or `TextureRect` that covers the screen:

```glsl
shader_type canvas_item;

// Godot 4 screen texture access
uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;

// Vignette
void fragment() {
    vec4 screen = texture(screen_texture, SCREEN_UV);
    float vignette = distance(SCREEN_UV, vec2(0.5));
    vignette = smoothstep(0.4, 0.8, vignette);
    screen.rgb *= 1.0 - vignette * 0.5;
    COLOR = screen;
}
```

### Controlling Shaders from GDScript
```gdscript
# Get the ShaderMaterial
var mat: ShaderMaterial = sprite.material as ShaderMaterial

# Set uniforms
mat.set_shader_parameter("flash_amount", 1.0)
mat.set_shader_parameter("dissolve_amount", 0.5)
mat.set_shader_parameter("tint_color", Color.RED)

# Animate shader parameters with tweens
var tween := create_tween()
tween.tween_method(
    func(val: float) -> void: mat.set_shader_parameter("flash_amount", val),
    1.0, 0.0, 0.3
)
```

### Performance Tips
- Avoid `discard` in fragment shaders when possible (breaks early-Z)
- Use `render_mode unshaded;` for UI shaders that don't need lighting
- Minimize texture samples in the fragment function
- Use `varying` to pass data from vertex to fragment (cheaper than recalculating)
- Use the shader baker (Godot 4.5+) to precompute static shader results into textures
