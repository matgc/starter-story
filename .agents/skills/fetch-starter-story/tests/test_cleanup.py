from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import cleanup  # noqa: E402


class CleanupTests(unittest.TestCase):
    def make_workspace(self, root: Path, name: str = "starter-story-sync-test") -> Path:
        workspace = root / "artifacts" / name
        workspace.mkdir(parents=True)
        (workspace / "manifest.json").write_text(
            json.dumps(
                {
                    "collector": cleanup.COLLECTOR_ID,
                    "channel": cleanup.EXPECTED_CHANNEL,
                }
            )
        )
        return workspace

    def test_repo_root_is_required_by_argparse(self) -> None:
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as raised:
            cleanup.parse_args(["starter-story-sync-test"])
        self.assertEqual(raised.exception.code, 2)

        args = cleanup.parse_args(["--repo-root", ".", "artifacts/starter-story-sync-test"])
        self.assertEqual(args.repo_root, Path("."))
        self.assertEqual(args.workspace, Path("artifacts/starter-story-sync-test"))

    def test_deletes_marked_direct_artifacts_child(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = self.make_workspace(root)
            expected = workspace.resolve()

            deleted = cleanup.cleanup_workspace(root, workspace)

            self.assertEqual(deleted, expected)
            self.assertFalse(workspace.exists())

    def test_rejects_path_outside_exact_repo_artifacts_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "repo"
            root.mkdir()
            outside = self.make_workspace(base / "outside")
            nested = self.make_workspace(root, "nested/starter-story-sync-test")

            for workspace in (outside, nested):
                with self.subTest(workspace=workspace), self.assertRaises(SystemExit):
                    cleanup.cleanup_workspace(root, workspace)
                self.assertTrue(workspace.exists())

    def test_rejects_bad_prefix_and_missing_or_wrong_collector_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bad_prefix = self.make_workspace(root, "other-sync-test")
            missing_marker = self.make_workspace(root, "starter-story-sync-missing")
            wrong_marker = self.make_workspace(root, "starter-story-sync-wrong")
            for workspace, marker in ((missing_marker, None), (wrong_marker, "another-collector")):
                manifest = workspace / "manifest.json"
                data = json.loads(manifest.read_text())
                if marker is None:
                    del data["collector"]
                else:
                    data["collector"] = marker
                manifest.write_text(json.dumps(data))

            for workspace in (bad_prefix, missing_marker, wrong_marker):
                with self.subTest(workspace=workspace), self.assertRaises(SystemExit):
                    cleanup.cleanup_workspace(root, workspace)
                self.assertTrue(workspace.exists())

    def test_rejects_symlink_workspace_or_parent_alias(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = self.make_workspace(root, "starter-story-sync-target")
            workspace = root / "artifacts" / "starter-story-sync-link"
            workspace.symlink_to(target, target_is_directory=True)
            parent_alias = root / "artifact-alias"
            parent_alias.symlink_to(root / "artifacts", target_is_directory=True)

            for path in (workspace, parent_alias / target.name):
                with self.subTest(path=path), self.assertRaises(SystemExit):
                    cleanup.cleanup_workspace(root, path)

            self.assertTrue(workspace.is_symlink())
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
