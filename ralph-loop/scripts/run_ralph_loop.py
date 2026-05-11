#!/usr/bin/env python3
"""Session manager for Ralph Loop style iterative coding workflows."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def inside_git_repo(workdir: Path) -> bool:
    probe = subprocess.run(
        "git rev-parse --is-inside-work-tree",
        cwd=str(workdir),
        shell=True,
        text=True,
        capture_output=True,
    )
    return probe.returncode == 0 and probe.stdout.strip() == "true"


def run_git(command: str, workdir: Path) -> str:
    result = subprocess.run(
        command,
        cwd=str(workdir),
        shell=True,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.rstrip()


def git_snapshot(workdir: Path) -> Dict[str, Any]:
    if not inside_git_repo(workdir):
        return {
            "available": False,
            "status_short": "",
            "diff_stat": "",
            "head": "",
        }
    return {
        "available": True,
        "status_short": run_git("git status --short", workdir),
        "diff_stat": run_git("git diff --stat", workdir),
        "head": run_git("git rev-parse --short HEAD", workdir),
    }


def default_state_file(workdir: Path) -> Path:
    return workdir / ".ralph-loop" / "session.json"


def load_task(args: argparse.Namespace) -> str:
    if args.task:
        return args.task.strip()
    task_file = Path(args.task_file).resolve()
    return task_file.read_text(encoding="utf-8").strip()


def load_state(state_file: Path, task: str, max_iterations: int) -> Dict[str, Any]:
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
        return state
    state_file.parent.mkdir(parents=True, exist_ok=True)
    return {
        "session_id": uuid.uuid4().hex[:12],
        "task": task,
        "max_iterations": max_iterations,
        "created_at": utc_now(),
        "history": [],
    }


def save_state(state_file: Path, state: Dict[str, Any]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def run_completion_check(
    script_path: Path,
    workdir: Path,
    commands: List[str],
    marker_file: Optional[str],
    marker_string: Optional[str],
    require_clean_git: bool,
    context_lines: int,
) -> Dict[str, Any]:
    with tempfile.NamedTemporaryFile(prefix="ralph-check-", suffix=".json", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    cmd = [
        sys.executable,
        str(script_path),
        "--workdir",
        str(workdir),
        "--context-lines",
        str(context_lines),
        "--json-out",
        str(tmp_path),
    ]
    for item in commands:
        cmd.extend(["--command", item])
    if marker_file:
        cmd.extend(["--marker-file", marker_file])
    if marker_string:
        cmd.extend(["--marker-string", marker_string])
    if require_clean_git:
        cmd.append("--require-clean-git")

    completed = subprocess.run(cmd, text=True, capture_output=True)
    summary = json.loads(tmp_path.read_text(encoding="utf-8"))
    tmp_path.unlink(missing_ok=True)
    summary["checker_exit_code"] = completed.returncode
    summary["checker_stdout"] = completed.stdout
    summary["checker_stderr"] = completed.stderr
    return summary


def primary_failure(summary: Dict[str, Any]) -> str:
    return summary.get("primary_failure") or "none"


def next_status(iteration: int, max_iterations: int, complete: bool) -> str:
    if complete:
        return "complete"
    if iteration >= max_iterations:
        return "budget-exhausted"
    return "continue"


def print_report(
    state: Dict[str, Any],
    iteration: int,
    status: str,
    completion: Dict[str, Any],
    git: Dict[str, Any],
    commands: List[str],
    state_file: Path,
) -> None:
    print(f"session_id: {state['session_id']}")
    print(f"iteration: {iteration}/{state['max_iterations']}")
    print(f"status: {status}")
    print(f"task: {state['task']}")
    print(f"state_file: {state_file}")
    print(f"primary_failure: {primary_failure(completion)}")
    print("verification:")
    if completion["commands"]:
        for item in completion["commands"]:
            outcome = "PASS" if item["passed"] else f"FAIL ({item['exit_code']})"
            print(f"- {item['command']}: {outcome}")
    else:
        print("- none configured")
    print(f"marker: {completion['marker']['reason']}")
    print("git:")
    if git["available"]:
        print(f"- head: {git['head']}")
        print(f"- clean: {'yes' if completion['git']['clean'] else 'no'}")
        if git["status_short"]:
            print("- status_short:")
            for line in git["status_short"].splitlines():
                print(f"    {line}")
        if git["diff_stat"]:
            print("- diff_stat:")
            for line in git["diff_stat"].splitlines():
                print(f"    {line}")
    else:
        print("- unavailable")
    print("next_action:")
    if status == "complete":
        print("- stop looping and report completion against the contract")
    elif status == "budget-exhausted":
        print("- stop automatic looping")
        print("- report the strongest blocker and the smallest concrete next step")
    else:
        print("- keep the task statement unchanged")
        print("- fix the primary failure with one focused batch of edits")
        print("- rerun this exact loop command")
    print("commands_to_repeat:")
    for command in commands:
        print(f"- {command}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    task_group = parser.add_mutually_exclusive_group(required=True)
    task_group.add_argument("--task", help="Stable task statement for the loop")
    task_group.add_argument("--task-file", help="File containing the stable task statement")
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
        "--max-iterations",
        type=int,
        default=8,
        help="Maximum number of loop iterations",
    )
    parser.add_argument(
        "--context-lines",
        type=int,
        default=20,
        help="Number of output tail lines to preserve per command",
    )
    parser.add_argument("--state-file", help="Optional custom session state path")
    parser.add_argument("--json-out", help="Optional output path for the updated session JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workdir = Path(args.workdir).resolve()
    if not workdir.exists() or not workdir.is_dir():
        print(f"error: workdir does not exist or is not a directory: {workdir}", file=sys.stderr)
        return 2
    if args.max_iterations < 1:
        print("error: --max-iterations must be at least 1", file=sys.stderr)
        return 2

    task = load_task(args)
    if not task:
        print("error: task statement is empty", file=sys.stderr)
        return 2

    state_file = Path(args.state_file).resolve() if args.state_file else default_state_file(workdir)
    state = load_state(state_file, task, args.max_iterations)

    if state.get("task") != task:
        print("error: task statement differs from existing session state", file=sys.stderr)
        return 2
    if int(state.get("max_iterations", args.max_iterations)) != args.max_iterations:
        state["max_iterations"] = args.max_iterations

    checker_script = Path(__file__).with_name("check_completion.py")
    completion = run_completion_check(
        script_path=checker_script,
        workdir=workdir,
        commands=args.command,
        marker_file=args.marker_file,
        marker_string=args.marker_string,
        require_clean_git=args.require_clean_git,
        context_lines=args.context_lines,
    )
    git = git_snapshot(workdir)

    iteration = len(state["history"]) + 1
    status = next_status(iteration, state["max_iterations"], completion["complete"])

    entry = {
        "iteration": iteration,
        "timestamp": utc_now(),
        "status": status,
        "completion": completion,
        "git": git,
        "commands": args.command,
        "marker_file": args.marker_file or "",
        "marker_string": args.marker_string or "",
        "require_clean_git": bool(args.require_clean_git),
    }
    state["history"].append(entry)
    state["updated_at"] = utc_now()
    save_state(state_file, state)

    if args.json_out:
        out_path = Path(args.json_out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    print_report(
        state=state,
        iteration=iteration,
        status=status,
        completion=completion,
        git=git,
        commands=args.command,
        state_file=state_file,
    )

    if status == "complete":
        return 0
    if status == "budget-exhausted":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
