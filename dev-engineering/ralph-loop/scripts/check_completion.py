#!/usr/bin/env python3
"""Deterministic completion checks for Ralph Loop style workflows."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def tail_lines(text: str, limit: int) -> str:
    lines = text.splitlines()
    if len(lines) <= limit:
        return text
    return "\n".join(lines[-limit:])


def run_command(command: str, workdir: Path, context_lines: int) -> Dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=str(workdir),
        shell=True,
        text=True,
        capture_output=True,
    )
    combined = "\n".join(
        part for part in [completed.stdout.rstrip(), completed.stderr.rstrip()] if part
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "tail": tail_lines(combined, context_lines),
    }


def inside_git_repo(workdir: Path) -> bool:
    probe = subprocess.run(
        "git rev-parse --is-inside-work-tree",
        cwd=str(workdir),
        shell=True,
        text=True,
        capture_output=True,
    )
    return probe.returncode == 0 and probe.stdout.strip() == "true"


def git_status(workdir: Path) -> Optional[str]:
    if not inside_git_repo(workdir):
        return None
    probe = subprocess.run(
        "git status --short",
        cwd=str(workdir),
        shell=True,
        text=True,
        capture_output=True,
    )
    if probe.returncode != 0:
        return None
    return probe.stdout


def check_marker(marker_file: Optional[Path], marker_string: Optional[str]) -> Dict[str, Any]:
    if marker_file is None:
        return {
            "configured": False,
            "passed": True,
            "reason": "no marker configured",
        }

    if not marker_file.exists():
        return {
            "configured": True,
            "passed": False,
            "reason": f"marker file not found: {marker_file}",
        }

    content = marker_file.read_text(encoding="utf-8")
    if marker_string and marker_string not in content:
        return {
            "configured": True,
            "passed": False,
            "reason": f"marker string not found in {marker_file}",
        }

    return {
        "configured": True,
        "passed": True,
        "reason": f"marker satisfied: {marker_file}",
    }


def build_summary(
    workdir: Path,
    command_results: List[Dict[str, Any]],
    marker_result: Dict[str, Any],
    require_clean_git: bool,
) -> Dict[str, Any]:
    git_short = git_status(workdir)
    git_clean = True if git_short is None else git_short.strip() == ""

    if not command_results and not marker_result["configured"] and not require_clean_git:
        raise ValueError("configure at least one command, marker check, or require-clean-git")

    failed_commands = [item for item in command_results if not item["passed"]]
    failed_reasons: List[str] = []
    if failed_commands:
        failed_reasons.append(f"{len(failed_commands)} command(s) failed")
    if not marker_result["passed"]:
        failed_reasons.append(marker_result["reason"])
    if require_clean_git and not git_clean:
        failed_reasons.append("git working tree is not clean")

    complete = not failed_reasons
    primary_failure = None
    if failed_commands:
        primary_failure = failed_commands[0]["command"]
    elif not marker_result["passed"]:
        primary_failure = marker_result["reason"]
    elif require_clean_git and not git_clean:
        primary_failure = "git working tree is not clean"

    return {
        "workdir": str(workdir),
        "complete": complete,
        "primary_failure": primary_failure,
        "failed_reasons": failed_reasons,
        "commands": [
            {
                "command": item["command"],
                "exit_code": item["exit_code"],
                "passed": item["passed"],
                "tail": item["tail"],
            }
            for item in command_results
        ],
        "marker": marker_result,
        "git": {
            "checked": True,
            "available": git_short is not None,
            "clean": git_clean,
            "status_short": git_short if git_short is not None else "",
        },
    }


def print_human_summary(summary: Dict[str, Any]) -> None:
    print(f"workdir: {summary['workdir']}")
    print(f"complete: {'yes' if summary['complete'] else 'no'}")
    print(f"primary_failure: {summary['primary_failure'] or 'none'}")
    print("commands:")
    if summary["commands"]:
        for item in summary["commands"]:
            status = "PASS" if item["passed"] else f"FAIL ({item['exit_code']})"
            print(f"- {item['command']}: {status}")
            if item["tail"]:
                for line in item["tail"].splitlines():
                    print(f"    {line}")
    else:
        print("- none configured")
    print(f"marker: {summary['marker']['reason']}")
    if summary["git"]["available"]:
        print(f"git_clean: {'yes' if summary['git']['clean'] else 'no'}")
        if summary["git"]["status_short"].strip():
            print("git_status:")
            for line in summary["git"]["status_short"].splitlines():
                print(f"  {line}")
    else:
        print("git_clean: unavailable")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", required=True, help="Repository or project directory")
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="Verification command to run. Repeat for multiple commands.",
    )
    parser.add_argument("--marker-file", help="Optional marker file path")
    parser.add_argument("--marker-string", help="Optional required string in the marker file")
    parser.add_argument(
        "--require-clean-git",
        action="store_true",
        help="Require a clean git working tree for completion",
    )
    parser.add_argument(
        "--context-lines",
        type=int,
        default=20,
        help="Number of output tail lines to keep for each command",
    )
    parser.add_argument("--json-out", help="Optional output path for summary JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workdir = Path(args.workdir).resolve()
    if not workdir.exists() or not workdir.is_dir():
        print(f"error: workdir does not exist or is not a directory: {workdir}", file=sys.stderr)
        return 2

    marker_file = Path(args.marker_file).resolve() if args.marker_file else None
    try:
        command_results = [run_command(cmd, workdir, args.context_lines) for cmd in args.command]
        marker_result = check_marker(marker_file, args.marker_string)
        summary = build_summary(
            workdir=workdir,
            command_results=command_results,
            marker_result=marker_result,
            require_clean_git=args.require_clean_git,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json_out:
        json_path = Path(args.json_out).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print_human_summary(summary)
    return 0 if summary["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
