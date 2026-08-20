from __future__ import annotations

import datetime as dt
import json
import sys
import tempfile
import unittest
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import classify  # noqa: E402


class CutoffTests(unittest.TestCase):
    def test_leap_day_clamps_to_february_28(self) -> None:
        self.assertEqual(classify.trailing_year_cutoff(dt.date(2024, 2, 29)), dt.date(2023, 2, 28))


class ClassificationTests(unittest.TestCase):
    @staticmethod
    def video_item(
        video_id: str,
        published: str,
        collection: str,
        filename: str | None = None,
    ) -> dict[str, str]:
        filename = filename or f"{published}-{video_id}.md"
        return {
            "video_id": video_id,
            "published": published,
            "title": f"Video {video_id}",
            "source": f"https://www.youtube.com/watch?v={video_id}",
            "path": f"kb/{collection}/{published[:4]}/{filename}",
        }

    @staticmethod
    def write_video(root: Path, path: str, content: str = "video\n") -> None:
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    @staticmethod
    def write_index(root: Path, items: Sequence[object]) -> Path:
        index = root / "kb" / "index.json"
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(json.dumps(items), encoding="utf-8")
        return index

    @staticmethod
    def tree_snapshot(root: Path) -> dict[str, bytes | None]:
        return {
            path.relative_to(root).as_posix(): None if path.is_dir() else path.read_bytes()
            for path in root.rglob("*")
        }

    @staticmethod
    def partial_write_interrupt_factory(
        real_named_temporary_file: Any, opened_handles: list[Any]
    ) -> Any:
        def open_interrupted_file(*args: Any, **kwargs: Any) -> Any:
            handle = real_named_temporary_file(*args, **kwargs)
            real_write = handle.write

            def interrupt_after_partial_write(content: Any) -> None:
                partial = content[: max(1, len(content) // 2)]
                real_write(partial)
                handle.flush()
                raise KeyboardInterrupt("temporary-file write interrupted")

            handle.write = interrupt_after_partial_write
            opened_handles.append(handle)
            return handle

        return open_interrupted_file

    def test_reclassifies_both_directions_rewrites_links_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stale_path = "kb/current/2025/2025-08-19-stale.md"
            boundary_path = "kb/historical/2025/2025-08-20-boundary.md"
            old_boundary = root / boundary_path
            self.write_video(root, stale_path, "[Note](../../links/note.md)\n")
            self.write_video(root, boundary_path, "boundary\n")
            unindexed_article = root / "kb" / "current" / "2024" / "article.md"
            unindexed_article.parent.mkdir(parents=True, exist_ok=True)
            unindexed_article.write_text("not video content\n", encoding="utf-8")
            link_note = root / "kb" / "links" / "note.md"
            link_note.parent.mkdir(parents=True, exist_ok=True)
            link_note.write_text("note\n", encoding="utf-8")
            strategy = root / "kb" / "strategies" / "overview.md"
            strategy.parent.mkdir(parents=True, exist_ok=True)
            strategy.write_text(
                "[Transcript](../current/2025/2025-08-19-stale.md#transcript)\n"
                "`[code](../current/2025/2025-08-19-stale.md)`\n"
                "````md\n"
                "[short fence](../current/2025/2025-08-19-stale.md)\n"
                "```\n"
                "[after short](../current/2025/2025-08-19-stale.md)\n"
                "~~~~\n"
                "[after other marker](../current/2025/2025-08-19-stale.md)\n"
                "````\n"
                "[after matching fence](../current/2025/2025-08-19-stale.md)\n",
                encoding="utf-8",
            )
            readme = root / "README.md"
            readme.write_text(
                "[Outer [nested label]](kb/current/2025/2025-08-19-stale.md)\n"
                "[Boundary](kb/historical/2025/2025-08-20-boundary.md)\n",
                encoding="utf-8",
            )
            index = self.write_index(
                root,
                [
                    self.video_item(
                        "boundary-video", "2025-08-20", "historical", "2025-08-20-boundary.md"
                    ),
                    self.video_item(
                        "stale-video", "2025-08-19", "current", "2025-08-19-stale.md"
                    ),
                ],
            )

            moved = classify.classify(root, dt.date(2026, 8, 20))

            archived = root / "kb" / "historical" / "2025" / "2025-08-19-stale.md"
            current_boundary = root / "kb" / "current" / "2025" / "2025-08-20-boundary.md"
            self.assertEqual(moved, 2)
            self.assertTrue(archived.is_file())
            self.assertTrue(current_boundary.is_file(), "the cutoff boundary is current")
            self.assertFalse(old_boundary.exists())
            self.assertTrue(unindexed_article.is_file(), "unindexed non-video content is never moved")
            updated_items = json.loads(index.read_text(encoding="utf-8"))
            self.assertEqual(updated_items[0]["path"], "kb/current/2025/2025-08-20-boundary.md")
            self.assertEqual(updated_items[1]["path"], "kb/historical/2025/2025-08-19-stale.md")
            self.assertIn(
                "[Outer [nested label]](kb/historical/2025/2025-08-19-stale.md)",
                readme.read_text(encoding="utf-8"),
            )
            self.assertIn(
                "[Boundary](kb/current/2025/2025-08-20-boundary.md)",
                readme.read_text(encoding="utf-8"),
            )
            strategy_text = strategy.read_text(encoding="utf-8")
            self.assertIn("(../historical/2025/2025-08-19-stale.md#transcript)", strategy_text)
            self.assertIn("`[code](../current/2025/2025-08-19-stale.md)`", strategy_text)
            self.assertIn("[short fence](../current/2025/2025-08-19-stale.md)", strategy_text)
            self.assertIn("[after short](../current/2025/2025-08-19-stale.md)", strategy_text)
            self.assertIn("[after other marker](../current/2025/2025-08-19-stale.md)", strategy_text)
            self.assertIn(
                "[after matching fence](../historical/2025/2025-08-19-stale.md)", strategy_text
            )
            self.assertEqual(archived.read_text(encoding="utf-8"), "[Note](../../links/note.md)\n")

            snapshot = self.tree_snapshot(root)
            self.assertEqual(classify.classify(root, dt.date(2026, 8, 20)), 0)
            self.assertEqual(snapshot, self.tree_snapshot(root))

    def test_requires_exact_nonempty_index_entry_shape(self) -> None:
        cases: list[tuple[str, dict[str, object], str]] = []
        missing_title: dict[str, object] = dict(
            self.video_item("v", "2025-01-01", "historical")
        )
        del missing_title["title"]
        cases.append(("missing-title", missing_title, "exactly the keys.*missing keys.*title"))
        extra_key: dict[str, object] = dict(
            self.video_item("v", "2025-01-01", "historical")
        )
        extra_key["duration"] = 1
        cases.append(("extra-key", extra_key, "exactly the keys.*extra keys.*duration"))
        blank_title: dict[str, object] = dict(
            self.video_item("v", "2025-01-01", "historical")
        )
        blank_title["title"] = "  "
        cases.append(("blank-title", blank_title, "non-empty string 'title'"))
        blank_source: dict[str, object] = dict(
            self.video_item("v", "2025-01-01", "historical")
        )
        blank_source["source"] = ""
        cases.append(("blank-source", blank_source, "non-empty string 'source'"))

        for name, item, message in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_video(root, str(item.get("path", "unused")))
                self.write_index(root, [item])
                with self.assertRaisesRegex(ValueError, message):
                    classify.classify(root, dt.date(2026, 8, 20))

    def test_rejects_every_malformed_index_record(self) -> None:
        malformed: list[tuple[str, object, str]] = [("non-object", "bad", "must be an object")]

        def changed(**values: str) -> dict[str, str]:
            item = self.video_item("v", "2025-01-01", "historical")
            item.update(values)
            return item

        malformed.extend(
            [
                ("blank-video-id", changed(video_id="   "), "video_id"),
                ("blank-published", changed(published=""), "published"),
                ("blank-path", changed(path=""), "path"),
                ("bad-published", changed(published="not-a-date"), "invalid published date"),
                (
                    "bad-collection",
                    changed(path="kb/videos/2025/2025-01-01-v.md"),
                    "invalid collection",
                ),
                (
                    "wrong-year",
                    changed(path="kb/historical/2024/2025-01-01-v.md"),
                    "does not match published year",
                ),
                (
                    "bad-suffix",
                    changed(path="kb/historical/2025/2025-01-01-v.txt"),
                    "named .md file",
                ),
                (
                    "traversal",
                    changed(path="kb/current/../2025/2025-01-01-v.md"),
                    "invalid path",
                ),
            ]
        )
        for name, item, message in malformed:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_index(root, [item])
                with self.assertRaisesRegex((ValueError, FileNotFoundError), message):
                    classify.classify(root, dt.date(2026, 8, 20))

    def test_rejects_filename_without_published_date_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = self.video_item("v", "2025-01-01", "historical", "wrong-name.md")
            self.write_video(root, item["path"])
            self.write_index(root, [item])

            with self.assertRaisesRegex(ValueError, "filename must start with published date"):
                classify.classify(root, dt.date(2026, 8, 20))

    def test_rejects_index_that_is_not_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            older = self.video_item("older", "2025-01-01", "historical")
            newer = self.video_item("newer", "2025-01-02", "historical")
            self.write_video(root, older["path"])
            self.write_video(root, newer["path"])
            self.write_index(root, [older, newer])

            with self.assertRaisesRegex(ValueError, "ordered newest first"):
                classify.classify(root, dt.date(2026, 8, 20))

    def test_rejects_duplicate_video_ids_and_paths(self) -> None:
        cases: list[tuple[str, list[dict[str, str]], str]] = [
            (
                "video-id",
                [
                    self.video_item("same", "2025-01-02", "historical"),
                    self.video_item("same", "2025-01-01", "historical"),
                ],
                "duplicate video_id",
            ),
            (
                "path",
                [
                    self.video_item("one", "2025-01-01", "historical"),
                    self.video_item("two", "2025-01-01", "historical", "2025-01-01-one.md"),
                ],
                "duplicate path",
            ),
        ]
        for name, items, message in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for item in items:
                    self.write_video(root, item["path"])
                self.write_index(root, items)
                with self.assertRaisesRegex(ValueError, message):
                    classify.classify(root, dt.date(2026, 8, 20))

    def test_rejects_path_that_resolves_outside_collection(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside_directory:
            root = Path(directory)
            outside = Path(outside_directory)
            (outside / "2025-01-01-v.md").write_text("outside\n", encoding="utf-8")
            current = root / "kb" / "current"
            current.mkdir(parents=True)
            (current / "2025").symlink_to(outside, target_is_directory=True)
            self.write_index(root, [self.video_item("v", "2025-01-01", "current")])

            with self.assertRaisesRegex(ValueError, "escapes its collection"):
                classify.classify(root, dt.date(2026, 8, 20))

    def test_rejects_forward_and_reverse_destination_collection_symlinks(self) -> None:
        cases = [
            ("forward", "current", "historical", "2025-01-01", dt.date(2026, 8, 20)),
            ("reverse", "historical", "current", "2025-08-20", dt.date(2026, 8, 20)),
        ]
        for name, source_collection, destination_collection, published, today in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                item = self.video_item("v", published, source_collection)
                self.write_video(root, item["path"])
                other = root / "other"
                other.mkdir()
                destination_root = root / "kb" / destination_collection
                destination_root.symlink_to("../other", target_is_directory=True)
                index = self.write_index(root, [item])
                before_index = index.read_bytes()

                with self.assertRaisesRegex(ValueError, "exact lexical root"):
                    classify.classify(root, today)

                self.assertTrue((root / item["path"]).is_file())
                self.assertFalse((other / published[:4] / Path(item["path"]).name).exists())
                self.assertEqual(index.read_bytes(), before_index)

    def test_rejects_collection_root_symlink_on_idempotent_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = self.video_item("v", "2025-08-20", "current")
            self.write_video(root, item["path"])
            other = root / "other"
            other.mkdir()
            (root / "kb" / "historical").symlink_to("../other", target_is_directory=True)
            self.write_index(root, [item])

            with self.assertRaisesRegex(ValueError, "exact lexical root"):
                classify.classify(root, dt.date(2026, 8, 20))

            self.assertTrue((root / item["path"]).is_file())

    def test_rejects_symlinked_index_before_migration(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            item = self.video_item("v", "2025-01-01", "current")
            self.write_video(root, item["path"])
            external_index = Path(outside) / "index.json"
            external_content = json.dumps([item]).encode()
            external_index.write_bytes(external_content)
            index = root / "kb" / "index.json"
            index.symlink_to(external_index)

            with self.assertRaisesRegex(ValueError, "index.json.*not a symlink"):
                classify.classify(root, dt.date(2026, 8, 20))

            self.assertTrue(index.is_symlink())
            self.assertEqual(external_index.read_bytes(), external_content)
            self.assertTrue((root / item["path"]).is_file())
            self.assertFalse(
                (root / "kb" / "historical" / "2025" / Path(item["path"]).name).exists()
            )

    def test_preflight_rejects_index_replaced_by_symlink_before_interruption(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            item = self.video_item("v", "2025-01-01", "current")
            self.write_video(root, item["path"])
            index = self.write_index(root, [item]).resolve()
            external_index = Path(outside) / "index.json"
            external_content = b"external\n"
            external_index.write_bytes(external_content)
            real_snapshot = classify._snapshot
            replaced = False

            def replace_index_after_snapshot(path: Path) -> classify.FileSnapshot:
                nonlocal replaced
                snapshot = real_snapshot(path)
                if path == index and not replaced:
                    replaced = True
                    index.unlink()
                    index.symlink_to(external_index)
                return snapshot

            with mock.patch.object(classify, "_snapshot", new=replace_index_after_snapshot):
                with mock.patch.object(
                    classify,
                    "atomic_write",
                    side_effect=KeyboardInterrupt("migration interrupted"),
                ) as atomic_write:
                    with self.assertRaisesRegex(ValueError, "index.json.*not a symlink"):
                        classify.classify(root, dt.date(2026, 8, 20))

            atomic_write.assert_not_called()
            self.assertTrue(replaced)
            self.assertTrue(index.is_symlink())
            self.assertEqual(external_index.read_bytes(), external_content)
            self.assertTrue((root / item["path"]).is_file())

    def test_rejects_symlink_component_below_destination_collection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = self.video_item("v", "2025-01-01", "current")
            self.write_video(root, item["path"])
            other = root / "other"
            other.mkdir()
            historical = root / "kb" / "historical"
            historical.mkdir()
            (historical / "2025").symlink_to("../../other", target_is_directory=True)
            self.write_index(root, [item])

            with self.assertRaisesRegex(ValueError, "must not traverse symlinks"):
                classify.classify(root, dt.date(2026, 8, 20))

            self.assertTrue((root / item["path"]).is_file())
            self.assertFalse((other / Path(item["path"]).name).exists())

    def make_two_move_repository(self, root: Path) -> None:
        one = self.video_item("one", "2025-01-02", "current")
        two = self.video_item("two", "2025-01-01", "current")
        self.write_video(root, one["path"], "one\n")
        self.write_video(root, two["path"], "two\n")
        readme = root / "README.md"
        readme.write_text(
            f"[One]({one['path']})\n[Two]({two['path']})\n",
            encoding="utf-8",
        )
        self.write_index(root, [one, two])

    def test_rechecks_destination_symlinks_before_each_rename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_two_move_repository(root)
            index = root / "kb" / "index.json"
            before_index = index.read_bytes()
            first_source = root / "kb" / "current" / "2025" / "2025-01-02-one.md"
            second_source = root / "kb" / "current" / "2025" / "2025-01-01-two.md"
            second_destination = root / "kb" / "historical" / "2025" / second_source.name
            attacker = root / "attacker.md"
            attacker.write_text("attacker\n", encoding="utf-8")
            real_rename = Path.rename
            calls = 0

            def add_symlink_after_first_rename(path: Path, target: Path) -> Path:
                nonlocal calls
                calls += 1
                result = real_rename(path, target)
                if calls == 1:
                    second_destination.symlink_to(attacker)
                return result

            with mock.patch.object(Path, "rename", new=add_symlink_after_first_rename):
                with self.assertRaisesRegex(ValueError, "must not traverse symlinks"):
                    classify.classify(root, dt.date(2026, 8, 20))

            self.assertTrue(first_source.is_file())
            self.assertTrue(second_source.is_file())
            self.assertTrue(second_destination.is_symlink())
            self.assertEqual(attacker.read_text(encoding="utf-8"), "attacker\n")
            self.assertEqual(index.read_bytes(), before_index)

    def test_rename_failure_rolls_back_all_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_two_move_repository(root)
            before = self.tree_snapshot(root)
            real_rename = Path.rename
            calls = 0

            def fail_second_rename(path: Path, target: Path) -> Path:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected rename failure")
                return real_rename(path, target)

            with mock.patch.object(Path, "rename", new=fail_second_rename):
                with self.assertRaisesRegex(OSError, "injected rename failure"):
                    classify.classify(root, dt.date(2026, 8, 20))

            self.assertEqual(before, self.tree_snapshot(root))

    def test_write_failure_rolls_back_renames_markdown_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_two_move_repository(root)
            before = self.tree_snapshot(root)
            index_path = (root / "kb" / "index.json").resolve()
            real_atomic_write = classify.atomic_write

            def fail_after_index_write(path: Path, content: str) -> None:
                real_atomic_write(path, content)
                if path == index_path:
                    raise OSError("injected write failure")

            with mock.patch.object(classify, "atomic_write", new=fail_after_index_write):
                with self.assertRaisesRegex(OSError, "injected write failure"):
                    classify.classify(root, dt.date(2026, 8, 20))

            self.assertEqual(before, self.tree_snapshot(root))

    def test_keyboard_interrupt_during_rename_rolls_back_and_reraises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_two_move_repository(root)
            before = self.tree_snapshot(root)
            real_rename = Path.rename
            calls = 0

            def interrupt_second_rename(path: Path, target: Path) -> Path:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise KeyboardInterrupt("rename interrupted")
                return real_rename(path, target)

            with mock.patch.object(Path, "rename", new=interrupt_second_rename):
                with self.assertRaisesRegex(KeyboardInterrupt, "rename interrupted"):
                    classify.classify(root, dt.date(2026, 8, 20))

            self.assertEqual(before, self.tree_snapshot(root))

    def test_keyboard_interrupt_during_markdown_write_rolls_back_and_reraises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_two_move_repository(root)
            before = self.tree_snapshot(root)
            index_path = (root / "kb" / "index.json").resolve()
            real_atomic_write = classify.atomic_write
            interrupted = False

            def interrupt_after_markdown_write(path: Path, content: str) -> None:
                nonlocal interrupted
                real_atomic_write(path, content)
                if path != index_path and not interrupted:
                    interrupted = True
                    raise KeyboardInterrupt("Markdown write interrupted")

            with mock.patch.object(classify, "atomic_write", new=interrupt_after_markdown_write):
                with self.assertRaisesRegex(KeyboardInterrupt, "Markdown write interrupted"):
                    classify.classify(root, dt.date(2026, 8, 20))

            self.assertTrue(interrupted)
            self.assertEqual(before, self.tree_snapshot(root))

    def test_keyboard_interrupt_during_index_write_rolls_back_and_reraises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_two_move_repository(root)
            before = self.tree_snapshot(root)
            index_path = (root / "kb" / "index.json").resolve()
            real_atomic_write = classify.atomic_write

            def interrupt_after_index_write(path: Path, content: str) -> None:
                real_atomic_write(path, content)
                if path == index_path:
                    raise KeyboardInterrupt("index write interrupted")

            with mock.patch.object(classify, "atomic_write", new=interrupt_after_index_write):
                with self.assertRaisesRegex(KeyboardInterrupt, "index write interrupted"):
                    classify.classify(root, dt.date(2026, 8, 20))

            self.assertEqual(before, self.tree_snapshot(root))

    def test_partial_markdown_write_interrupt_cleans_temp_and_rolls_back(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_two_move_repository(root)
            before = self.tree_snapshot(root)
            index_path = (root / "kb" / "index.json").resolve()
            real_atomic_write = classify.atomic_write
            real_named_temporary_file = classify.tempfile.NamedTemporaryFile
            opened_handles: list[Any] = []
            interrupted = False

            def interrupt_markdown_write(path: Path, content: str) -> None:
                nonlocal interrupted
                if path != index_path and not interrupted:
                    interrupted = True
                    factory = self.partial_write_interrupt_factory(
                        real_named_temporary_file, opened_handles
                    )
                    with mock.patch.object(
                        classify.tempfile, "NamedTemporaryFile", new=factory
                    ):
                        real_atomic_write(path, content)
                    return
                real_atomic_write(path, content)

            with mock.patch.object(classify, "atomic_write", new=interrupt_markdown_write):
                with self.assertRaisesRegex(KeyboardInterrupt, "temporary-file write interrupted"):
                    classify.classify(root, dt.date(2026, 8, 20))

            self.assertTrue(interrupted)
            self.assertTrue(opened_handles)
            self.assertTrue(all(handle.closed for handle in opened_handles))
            self.assertEqual(before, self.tree_snapshot(root))

    def test_partial_index_write_interrupt_cleans_temp_and_rolls_back(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_two_move_repository(root)
            before = self.tree_snapshot(root)
            index_path = (root / "kb" / "index.json").resolve()
            real_atomic_write = classify.atomic_write
            real_named_temporary_file = classify.tempfile.NamedTemporaryFile
            opened_handles: list[Any] = []

            def interrupt_index_write(path: Path, content: str) -> None:
                if path == index_path:
                    factory = self.partial_write_interrupt_factory(
                        real_named_temporary_file, opened_handles
                    )
                    with mock.patch.object(
                        classify.tempfile, "NamedTemporaryFile", new=factory
                    ):
                        real_atomic_write(path, content)
                    return
                real_atomic_write(path, content)

            with mock.patch.object(classify, "atomic_write", new=interrupt_index_write):
                with self.assertRaisesRegex(KeyboardInterrupt, "temporary-file write interrupted"):
                    classify.classify(root, dt.date(2026, 8, 20))

            self.assertTrue(opened_handles)
            self.assertTrue(all(handle.closed for handle in opened_handles))
            self.assertEqual(before, self.tree_snapshot(root))

    def test_partial_restore_write_interrupt_cleans_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "file.md"
            target.write_text("original\n", encoding="utf-8")
            snapshot = classify._snapshot(target)
            target.write_text("changed\n", encoding="utf-8")
            real_named_temporary_file = classify.tempfile.NamedTemporaryFile
            opened_handles: list[Any] = []
            factory = self.partial_write_interrupt_factory(
                real_named_temporary_file, opened_handles
            )

            with mock.patch.object(classify.tempfile, "NamedTemporaryFile", new=factory):
                with self.assertRaisesRegex(KeyboardInterrupt, "temporary-file write interrupted"):
                    classify._restore(target, snapshot)

            self.assertTrue(opened_handles)
            self.assertTrue(all(handle.closed for handle in opened_handles))
            self.assertEqual(target.read_text(encoding="utf-8"), "changed\n")
            self.assertEqual(list(root.iterdir()), [target])


if __name__ == "__main__":
    unittest.main()
