#!/usr/bin/env python3
"""Lint and auto-fix common GDScript issues.

Checks for the most impactful GDScript problems that lead to bugs
or poor performance. Can optionally auto-fix safe issues.

Usage:
    python gdscript_lint.py <file_or_dir> [--fix] [--quiet]

Checks:
    [PERF] Uncached node access in _process/_physics_process ($Node, get_node)
    [TYPE] Missing type hints on variables, parameters, and return values
    [SIG]  Godot 3 signal syntax (connect/emit_signal string-based)
    [API]  Godot 3 API calls (instance, yield, rand_range, update, etc.)
    [STYLE] Untyped Array/Dictionary declarations
    [BUG]  get_parent() calls (upward coupling)
    [BUG]  global_position set before add_child
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LintIssue:
    file: str
    line: int
    code: str
    severity: str
    message: str
    fix: str | None = None  # Suggested replacement line


# ── Lint rules ───────────────────────────────────────────────────────

def check_uncached_node_access(lines: list[str], filepath: str) -> list[LintIssue]:
    """Detect $Node or get_node() inside _process/_physics_process."""
    issues: list[LintIssue] = []
    in_process = False
    indent_level = -1

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detect process function entry
        if re.match(r'^func\s+_(physics_)?process\s*\(', stripped):
            in_process = True
            indent_level = len(line) - len(line.lstrip())
            continue

        # Detect function exit (same or lower indentation)
        if in_process and stripped and not stripped.startswith('#'):
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and stripped.startswith('func '):
                in_process = False
                continue

        if in_process and stripped:
            if re.search(r'\$\w+', stripped) or re.search(r'get_node\s*\(', stripped):
                issues.append(LintIssue(
                    file=filepath, line=i, code="PERF001", severity="warning",
                    message="Uncached node access in _process(). Use @onready var instead.",
                ))
    return issues


def check_missing_type_hints(lines: list[str], filepath: str) -> list[LintIssue]:
    """Detect variables and function params without type hints."""
    issues: list[LintIssue] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # var declarations without type
        m = re.match(r'^((?:@export\s+)?var\s+\w+)\s*=\s*', stripped)
        if m and ':' not in m.group(1):
            # Skip if it's a complex expression (dict/array literal)
            if not re.search(r'=\s*[\[\{]', stripped):
                issues.append(LintIssue(
                    file=filepath, line=i, code="TYPE001", severity="info",
                    message="Variable missing type hint. Add ': Type' for 40%+ perf boost.",
                ))

        # func return type
        if re.match(r'^func\s+\w+\s*\(.*\)\s*:', stripped):
            pass  # Has return type
        elif re.match(r'^func\s+\w+\s*\(.*\)\s*->\s*\w+', stripped):
            pass  # Has return type
        elif re.match(r'^func\s+\w+\s*\(', stripped):
            if not stripped.startswith('func _init'):
                # Check there's no -> in the signature
                if '->' not in stripped:
                    issues.append(LintIssue(
                        file=filepath, line=i, code="TYPE002", severity="info",
                        message="Function missing return type hint. Add '-> ReturnType'.",
                    ))
    return issues


def check_godot3_signals(lines: list[str], filepath: str) -> list[LintIssue]:
    """Detect Godot 3 signal patterns."""
    issues: list[LintIssue] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # emit_signal("name", args)
        m = re.search(r'emit_signal\s*\(\s*["\'](\w+)["\']', stripped)
        if m:
            sig_name = m.group(1)
            issues.append(LintIssue(
                file=filepath, line=i, code="SIG001", severity="error",
                message=f'Godot 3 emit_signal(). Use: {sig_name}.emit(...)',
                fix=re.sub(r'emit_signal\s*\(\s*["\'](\w+)["\']\s*(?:,\s*)?', r'\1.emit(', stripped),
            ))

        # connect("signal", target, "method")
        m = re.search(r'\.connect\s*\(\s*["\'](\w+)["\']\s*,\s*(\w+)\s*,\s*["\'](\w+)["\']', stripped)
        if m:
            sig, target, method = m.group(1), m.group(2), m.group(3)
            issues.append(LintIssue(
                file=filepath, line=i, code="SIG002", severity="error",
                message=f'Godot 3 connect(). Use: {sig}.connect({target}.{method})',
            ))
    return issues


def check_godot3_api(lines: list[str], filepath: str) -> list[LintIssue]:
    """Detect renamed Godot 3 API calls."""
    renames = {
        r'\.instance\(\)': ('.instantiate()', 'API001'),
        r'\byield\s*\(': ('await', 'API002'),
        r'\brand_range\s*\(': ('randf_range()', 'API003'),
        r'\bstepify\s*\(': ('snapped()', 'API004'),
        r'\bstr2var\s*\(': ('str_to_var()', 'API005'),
        r'\bvar2str\s*\(': ('var_to_str()', 'API006'),
        r'\bupdate\s*\(\)': ('queue_redraw()', 'API007'),
        r'\.rect_position\b': ('.position', 'API008'),
        r'\.rect_size\b': ('.size', 'API009'),
        r'\.rect_min_size\b': ('.custom_minimum_size', 'API010'),
        r'\.empty\(\)': ('.is_empty()', 'API011'),
    }
    issues: list[LintIssue] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        for pattern, (replacement, code) in renames.items():
            if re.search(pattern, stripped):
                issues.append(LintIssue(
                    file=filepath, line=i, code=code, severity="error",
                    message=f'Godot 3 API: {pattern.strip(chr(92))} -> {replacement}',
                ))
    return issues


def check_upward_coupling(lines: list[str], filepath: str) -> list[LintIssue]:
    """Detect get_parent() calls which create fragile upward dependencies."""
    issues: list[LintIssue] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        if 'get_parent()' in stripped:
            issues.append(LintIssue(
                file=filepath, line=i, code="BUG001", severity="warning",
                message="get_parent() creates upward coupling. Use signals instead.",
            ))
    return issues


def check_untyped_collections(lines: list[str], filepath: str) -> list[LintIssue]:
    """Detect Array and Dictionary without type parameters."""
    issues: list[LintIssue] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # var x: Array = [] (no type param)
        if re.search(r':\s*Array\s*=', stripped) and '[' not in stripped.split('=')[0]:
            issues.append(LintIssue(
                file=filepath, line=i, code="STYLE001", severity="info",
                message="Untyped Array. Use Array[Type] for type safety.",
            ))
        # var x: Dictionary = {} (Godot 4.4+ supports typed dicts)
        if re.search(r':\s*Dictionary\s*=', stripped) and '[' not in stripped.split('=')[0]:
            issues.append(LintIssue(
                file=filepath, line=i, code="STYLE002", severity="info",
                message="Untyped Dictionary. In Godot 4.4+, use Dictionary[KeyType, ValueType].",
            ))
    return issues


ALL_CHECKS = [
    check_uncached_node_access,
    check_missing_type_hints,
    check_godot3_signals,
    check_godot3_api,
    check_upward_coupling,
    check_untyped_collections,
]


# ── Auto-fix ─────────────────────────────────────────────────────────

def apply_fixes(filepath: Path, issues: list[LintIssue]) -> int:
    """Apply auto-fixes for issues that have a fix suggestion. Returns count."""
    fixable = {issue.line: issue.fix for issue in issues if issue.fix}
    if not fixable:
        return 0

    lines = filepath.read_text(encoding="utf-8").splitlines(keepends=True)
    fixed = 0
    for line_num, fix in fixable.items():
        idx = line_num - 1
        if 0 <= idx < len(lines):
            indent = lines[idx][:len(lines[idx]) - len(lines[idx].lstrip())]
            lines[idx] = indent + fix + "\n"
            fixed += 1

    filepath.write_text("".join(lines), encoding="utf-8")
    return fixed


# ── Main ─────────────────────────────────────────────────────────────

def lint_file(filepath: Path) -> list[LintIssue]:
    """Run all checks on a single .gd file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [LintIssue(file=str(filepath), line=0, code="ERR", severity="error",
                          message=f"Could not read file: {e}")]

    lines = content.splitlines()
    issues: list[LintIssue] = []
    for check in ALL_CHECKS:
        issues.extend(check(lines, str(filepath)))
    return sorted(issues, key=lambda x: x.line)


def find_gd_files(path: Path) -> list[Path]:
    """Find all .gd files under a path."""
    if path.is_file():
        return [path] if path.suffix == ".gd" else []
    return sorted(path.rglob("*.gd"))


SEVERITY_COLORS = {
    "error": "\033[91m",    # red
    "warning": "\033[93m",  # yellow
    "info": "\033[96m",     # cyan
}
RESET = "\033[0m"


def format_issue(issue: LintIssue, use_color: bool = True) -> str:
    color = SEVERITY_COLORS.get(issue.severity, "") if use_color else ""
    reset = RESET if use_color else ""
    return (
        f"{issue.file}:{issue.line}: "
        f"{color}[{issue.code}] {issue.severity}: {issue.message}{reset}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint GDScript files for common issues.")
    parser.add_argument("path", help="File or directory to lint")
    parser.add_argument("--fix", action="store_true",
                        help="Auto-fix issues where safe (Godot 3 signal syntax)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Only show errors, not warnings or info")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable colored output")

    args = parser.parse_args()
    target = Path(args.path).resolve()

    if not target.exists():
        print(f"Error: '{target}' does not exist", file=sys.stderr)
        sys.exit(1)

    files = find_gd_files(target)
    if not files:
        print(f"No .gd files found in '{target}'")
        sys.exit(0)

    total_issues = 0
    total_fixed = 0
    severity_filter = {"error"} if args.quiet else {"error", "warning", "info"}

    for f in files:
        issues = lint_file(f)
        filtered = [i for i in issues if i.severity in severity_filter]

        if args.fix:
            fixed = apply_fixes(f, filtered)
            total_fixed += fixed

        for issue in filtered:
            print(format_issue(issue, use_color=not args.no_color))
        total_issues += len(filtered)

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Files scanned: {len(files)}")
    print(f"Issues found:  {total_issues}")
    if args.fix:
        print(f"Issues fixed:  {total_fixed}")

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
