#!/usr/bin/env python3
"""Generate a standard Godot 4.x project directory structure.

Creates project.godot, .gitignore, recommended folders, and optional
autoload scripts (GameManager, EventBus, SceneManager).

Usage:
    python scaffold_project.py <project_name> [--path <dir>] [--with-autoloads] [--small]
"""

import argparse
import os
import sys
from pathlib import Path

# ── Directory layouts ─────────────────────────────────────────────────

FULL_DIRS = [
    "scenes/levels",
    "scenes/entities/player",
    "scenes/entities/enemies",
    "scenes/ui",
    "scenes/components",
    "scripts/autoloads",
    "scripts/resources",
    "scripts/utils",
    "resources/themes",
    "assets/sprites/player",
    "assets/sprites/enemies",
    "assets/sprites/tiles",
    "assets/sprites/ui",
    "assets/audio/music",
    "assets/audio/sfx",
    "assets/fonts",
    "assets/shaders",
    "addons",
]

SMALL_DIRS = [
    "sprites",
    "audio",
    "shaders",
]

# ── Template contents ────────────────────────────────────────────────

GITIGNORE = """\
# Godot 4
.godot/

# Mono/C#
.mono/
data_*/
mono_crash.*.json

# Export builds
build/
export/

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/
*.code-workspace
"""


def project_godot(name: str, autoloads: dict[str, str] | None = None) -> str:
    lines = [
        "; Engine configuration file.",
        "; It's best edited using the editor UI and not directly,",
        "; since the parameters that go here are not all obvious.",
        ";",
        "; Format:",
        ";   [section] ; section goes between []",
        ";   param=value ; assign values to parameters",
        "",
        "config_version=5",
        "",
        "[application]",
        "",
        f'config/name="{name}"',
        'run/main_scene="res://scenes/main.tscn"',
        'config/features=PackedStringArray("4.4")',
    ]

    if autoloads:
        lines += ["", "[autoload]", ""]
        for cls, path in autoloads.items():
            lines.append(f'{cls}="*res://{path}"')

    lines += [
        "",
        "[display]",
        "",
        "window/size/viewport_width=1280",
        "window/size/viewport_height=720",
        'window/stretch/mode="canvas_items"',
        'window/stretch/aspect="keep"',
        "",
        "[layer_names]",
        "",
        '2d_physics/layer_1="Player"',
        '2d_physics/layer_2="Enemies"',
        '2d_physics/layer_3="Environment"',
        '2d_physics/layer_4="Projectiles"',
        "",
    ]
    return "\n".join(lines)


MAIN_SCENE = """\
[gd_scene format=3]

[node name="Main" type="Node2D"]
"""

GAME_MANAGER = """\
extends Node
## Global game state and settings.
##
## Autoload singleton — access via GameManager anywhere.

var score: int = 0
var is_paused: bool = false


func reset() -> void:
\tscore = 0
\tis_paused = false
"""

EVENT_BUS = """\
extends Node
## Global event bus for decoupled communication.
##
## Autoload singleton — connect to these signals from anywhere.
## Use sparingly; prefer direct signals for local communication.

signal player_died
signal score_changed(new_score: int)
signal level_completed(level_id: int)
signal game_over
"""

SCENE_MANAGER = """\
extends Node
## Handles scene transitions with optional fade effect.
##
## Autoload singleton — call SceneManager.change_scene("res://...").

var _current_scene: Node = null


func _ready() -> void:
\tvar root: Window = get_tree().root
\t_current_scene = root.get_child(root.get_child_count() - 1)


func change_scene(path: String) -> void:
\tcall_deferred("_deferred_change_scene", path)


func _deferred_change_scene(path: String) -> void:
\t_current_scene.free()
\tvar next_scene: PackedScene = ResourceLoader.load(path)
\t_current_scene = next_scene.instantiate()
\tget_tree().root.add_child(_current_scene)
\tget_tree().current_scene = _current_scene
"""

AUTOLOADS: dict[str, tuple[str, str]] = {
    "GameManager": ("scripts/autoloads/game_manager.gd", GAME_MANAGER),
    "EventBus": ("scripts/autoloads/event_bus.gd", EVENT_BUS),
    "SceneManager": ("scripts/autoloads/scene_manager.gd", SCENE_MANAGER),
}


# ── Scaffolding logic ───────────────────────────────────────────────

def scaffold(project_name: str, base: Path, small: bool, with_autoloads: bool) -> list[str]:
    """Create directory structure and files. Returns list of created paths."""
    created: list[str] = []
    root = base / project_name
    root.mkdir(parents=True, exist_ok=True)

    # Directories
    dirs = SMALL_DIRS if small else FULL_DIRS
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)
        created.append(f"  {d}/")

    # .gitignore
    _write(root / ".gitignore", GITIGNORE, created)

    # Autoloads
    autoload_map: dict[str, str] | None = None
    if with_autoloads and not small:
        autoload_map = {}
        for cls, (path, content) in AUTOLOADS.items():
            _write(root / path, content, created)
            autoload_map[cls] = path

    # project.godot
    _write(root / "project.godot", project_godot(project_name, autoload_map), created)

    # Main scene
    scene_dir = "scenes" if not small else ""
    main_path = root / scene_dir / "main.tscn" if scene_dir else root / "main.tscn"
    main_path.parent.mkdir(parents=True, exist_ok=True)
    _write(main_path, MAIN_SCENE, created)

    return created


def _write(path: Path, content: str, created: list[str]) -> None:
    path.write_text(content, encoding="utf-8")
    created.append(f"  {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a Godot 4.x project directory structure."
    )
    parser.add_argument("project_name", help="Name of the project (becomes folder name)")
    parser.add_argument("--path", default=".", help="Parent directory (default: current dir)")
    parser.add_argument("--with-autoloads", action="store_true",
                        help="Generate GameManager, EventBus, SceneManager autoloads")
    parser.add_argument("--small", action="store_true",
                        help="Use flat layout for small projects/prototypes")

    args = parser.parse_args()
    base = Path(args.path).resolve()

    if not base.exists():
        print(f"Error: path '{base}' does not exist", file=sys.stderr)
        sys.exit(1)

    created = scaffold(args.project_name, base, args.small, args.with_autoloads)

    print(f"Created Godot project '{args.project_name}' at {base / args.project_name}")
    print(f"Files and directories created ({len(created)}):")
    for item in created:
        print(item)


if __name__ == "__main__":
    main()
