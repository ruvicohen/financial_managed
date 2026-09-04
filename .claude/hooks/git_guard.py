#!/usr/bin/env python3
"""PreToolUse guard for the Bash tool.

Enforces this project's Git Workflow (see CLAUDE.md): never commit or push
directly to main, never stage secret/.env files. Reads the pending tool call
as JSON on stdin; on violation, emits a PreToolUse "deny" decision as JSON on
stdout. Otherwise exits silently (0) to allow the command through.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

SECRET_SUFFIXES = (".pem", ".key")
SECRET_BASENAMES = ("id_rsa", "id_ed25519")


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def is_secret_path(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    if name == ".env.example":
        return False
    if name == ".env" or name.startswith(".env."):
        return True
    if name in SECRET_BASENAMES:
        return True
    return name.endswith(SECRET_SUFFIXES)


def current_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()
    except OSError:
        return ""


def working_tree_secret_paths() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    paths = []
    for line in result.stdout.splitlines():
        # porcelain format: "XY path" (path may contain spaces after col 3)
        path = line[3:].strip()
        if path:
            paths.append(path)
    return paths


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return

    command = payload.get("tool_input", {}).get("command", "") or ""
    if not re.search(r"\bgit\b", command):
        return

    branch = current_branch()

    # --- 1. Block committing directly on main ---
    if re.search(r"\bgit\s+commit\b", command) and branch == "main":
        deny(
            "Blocked: never commit directly on main. Create a feature branch "
            "first (e.g. git checkout -b feat/your-change), per the Git "
            "Workflow in CLAUDE.md."
        )

    # --- 2. Block pushing to main ---
    push_match = re.search(r"\bgit\s+push\b(.*)", command)
    if push_match:
        push_rest = push_match.group(1)
        explicit_main = re.search(r"(^|[\s/:])main([\s]|$)", push_rest) or re.search(
            r"refs/heads/main([\s]|$)", push_rest
        )
        if explicit_main:
            deny(
                "Blocked: never push directly to main. Push a feature branch "
                "and open a Pull Request instead, per the Git Workflow in "
                "CLAUDE.md."
            )
        feature_prefix = re.search(
            r"[\s](feat|fix|chore|docs|refactor|test|ci|build|perf)/", push_rest
        )
        if branch == "main" and not feature_prefix:
            deny(
                "Blocked: currently on main and this push does not target a "
                "feature branch. Push a feature branch and open a Pull "
                "Request instead, per the Git Workflow in CLAUDE.md."
            )

    # --- 3. Block staging/committing files that look like secrets ---
    add_match = re.search(r"\bgit\s+add\s+(.*)", command)
    if add_match:
        add_args = add_match.group(1)
        tokens = add_args.split()
        broad_add = any(t in ("-A", "--all", ".") for t in tokens)
        if broad_add:
            for path in working_tree_secret_paths():
                if is_secret_path(path):
                    deny(
                        f"Blocked: '{command}' would stage '{path}', which "
                        "looks like a secret/.env file. Never commit secrets "
                        "or .env files, per the Git Workflow in CLAUDE.md."
                    )
        else:
            for token in tokens:
                if token.startswith("-"):
                    continue
                if is_secret_path(token):
                    deny(
                        f"Blocked: '{command}' would stage '{token}', which "
                        "looks like a secret/.env file. Never commit secrets "
                        "or .env files, per the Git Workflow in CLAUDE.md."
                    )

    if re.search(r"\bgit\s+commit\b[^|&;]*(-a\b|-am\b|--all\b)", command):
        for path in working_tree_secret_paths():
            if is_secret_path(path):
                deny(
                    f"Blocked: '{command}' (commit -a) would include "
                    f"'{path}', which looks like a secret/.env file. Never "
                    "commit secrets or .env files, per the Git Workflow in "
                    "CLAUDE.md."
                )


if __name__ == "__main__":
    main()
