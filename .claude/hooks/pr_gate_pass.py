#!/usr/bin/env python3
"""Record that the pre-PR review gate passed for the current branch at HEAD.

The pre-PR review gate (see CLAUDE.md) is: run /security-review and
/code-review on the branch diff against main, then fix or record every
blocking finding. After that, run this script.

It writes .claude/.pr-gate/<branch>.sha containing the current HEAD commit.
The Bash PreToolUse guard (.claude/hooks/git_guard.py) reads that marker and
interrupts a feature-branch `git push` for confirmation until it matches the
commit being pushed.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()


def main() -> int:
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    head = _git("rev-parse", "HEAD")
    if not branch or not head or branch == "HEAD":
        print("Not on a branch in a git repository.", file=sys.stderr)
        return 1

    marker_dir = pathlib.Path(".claude/.pr-gate")
    marker_dir.mkdir(parents=True, exist_ok=True)
    marker = marker_dir / f"{branch.replace('/', '__')}.sha"
    marker.write_text(head + "\n", encoding="utf-8")

    print(f"Pre-PR review gate recorded for {branch} @ {head[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
