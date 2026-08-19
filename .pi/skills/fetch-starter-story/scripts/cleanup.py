#!/usr/bin/env python3
"""Delete only a collection workspace created by collect.py."""

import json
import shutil
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: cleanup.py <workspace>")
workspace = Path(sys.argv[1]).resolve()
manifest = workspace / "manifest.json"
if workspace.parent.name != "artifacts" or not workspace.name.startswith("starter-story-sync-"):
    raise SystemExit(f"refusing to delete unexpected path: {workspace}")
if not manifest.is_file():
    raise SystemExit(f"refusing to delete workspace without manifest: {workspace}")
data = json.loads(manifest.read_text())
if data.get("channel") != "https://www.youtube.com/@starterstory/videos":
    raise SystemExit("refusing to delete workspace with an unexpected channel")
shutil.rmtree(workspace)
print(f"Deleted {workspace}")
