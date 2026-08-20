#!/usr/bin/env python3
"""Delete only a collection workspace created by collect.py."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Sequence

COLLECTOR_ID = "fetch-starter-story"
EXPECTED_CHANNEL = "https://www.youtube.com/@starterstory/videos"
WORKSPACE_PREFIX = "starter-story-sync-"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("workspace", type=Path)
    return parser.parse_args(argv)


def cleanup_workspace(repo_root_path: Path, workspace_path: Path) -> Path:
    unresolved_repo_root = Path(os.path.abspath(repo_root_path))
    repo_root = repo_root_path.resolve()
    expected_parent = repo_root / "artifacts"
    unresolved_workspace = Path(os.path.abspath(workspace_path))

    if unresolved_workspace.parent != unresolved_repo_root / "artifacts":
        raise SystemExit(f"refusing to delete non-direct workspace path: {unresolved_workspace}")
    if unresolved_workspace.is_symlink():
        raise SystemExit(f"refusing to delete symlink workspace: {unresolved_workspace}")

    workspace = unresolved_workspace.resolve()
    if workspace.parent != expected_parent or not workspace.name.startswith(WORKSPACE_PREFIX):
        raise SystemExit(f"refusing to delete unexpected path: {workspace}")
    if not workspace.is_dir():
        raise SystemExit(f"refusing to delete non-directory workspace: {workspace}")

    manifest = workspace / "manifest.json"
    if manifest.is_symlink() or not manifest.is_file():
        raise SystemExit(f"refusing to delete workspace without a regular manifest: {workspace}")
    try:
        data = json.loads(manifest.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"refusing to delete workspace with an invalid manifest: {error}") from error
    if not isinstance(data, dict) or data.get("collector") != COLLECTOR_ID:
        raise SystemExit("refusing to delete workspace with an unexpected collector marker")
    if data.get("channel") != EXPECTED_CHANNEL:
        raise SystemExit("refusing to delete workspace with an unexpected channel")

    shutil.rmtree(workspace)
    return workspace


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    workspace = cleanup_workspace(args.repo_root, args.workspace)
    print(f"Deleted {workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
