#!/usr/bin/env python3
"""Move indexed video Markdown between the current and historical archives."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote, unquote, urlsplit, urlunsplit

REFERENCE_LINK_RE = re.compile(
    r"^(?P<prefix>[ \t]{0,3}\[[^\]\n]+\]:[ \t]*)(?P<target><[^>\n]+>|\S+)", re.MULTILINE
)
FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})(?P<rest>[^\r\n]*)")

FileSnapshot = tuple[bytes, int]
Move = tuple[Path, Path]
INDEX_FIELDS = frozenset({"video_id", "published", "title", "source", "path"})


def trailing_year_cutoff(today: dt.date) -> dt.date:
    """Return the same calendar date one year earlier, clamping leap day."""
    try:
        return today.replace(year=today.year - 1)
    except ValueError:
        return today.replace(year=today.year - 1, day=28)


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _required_string(item: dict[str, Any], field: str, position: int) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"kb/index.json item {position} requires a non-empty string {field!r}")
    return value


def validate_video_item(
    repo_root: Path, item: object, position: int
) -> tuple[dict[str, Any], str, dt.date, Path, str]:
    """Validate one index record and return its normalized classification data."""
    if not isinstance(item, dict):
        raise ValueError(f"kb/index.json item {position} must be an object")

    item_fields = set(item)
    if item_fields != INDEX_FIELDS:
        missing = sorted(INDEX_FIELDS - item_fields)
        extra = sorted(str(field) for field in item_fields - INDEX_FIELDS)
        details: list[str] = []
        if missing:
            details.append(f"missing keys {missing}")
        if extra:
            details.append(f"extra keys {extra}")
        raise ValueError(
            f"kb/index.json item {position} must have exactly the keys "
            f"{sorted(INDEX_FIELDS)} ({'; '.join(details)})"
        )

    video_id = _required_string(item, "video_id", position)
    published_text = _required_string(item, "published", position)
    _required_string(item, "title", position)
    _required_string(item, "source", position)
    path_text = _required_string(item, "path", position)

    try:
        published = dt.date.fromisoformat(published_text)
    except ValueError as error:
        raise ValueError(
            f"kb/index.json item {position} video {video_id!r} has invalid published date "
            f"{published_text!r}"
        ) from error
    if published.isoformat() != published_text:
        raise ValueError(
            f"kb/index.json item {position} video {video_id!r} published must use YYYY-MM-DD"
        )

    relative = PurePosixPath(path_text)
    if relative.is_absolute() or relative.as_posix() != path_text or len(relative.parts) != 4:
        raise ValueError(
            f"kb/index.json item {position} video {video_id!r} has invalid path {path_text!r}; "
            "expected kb/current/YYYY/name.md or kb/historical/YYYY/name.md"
        )
    if relative.parts[0] != "kb" or relative.parts[1] not in {"current", "historical"}:
        raise ValueError(
            f"kb/index.json item {position} video {video_id!r} path has invalid collection; "
            "expected 'current' or 'historical'"
        )
    year = relative.parts[2]
    if len(year) != 4 or not year.isdecimal() or int(year) != published.year:
        raise ValueError(
            f"kb/index.json item {position} video {video_id!r} path year {year!r} "
            f"does not match published year {published.year}"
        )
    if relative.suffix != ".md" or not relative.stem:
        raise ValueError(
            f"kb/index.json item {position} video {video_id!r} path must end in a named .md file"
        )
    if not relative.name.startswith(f"{published_text}-"):
        raise ValueError(
            f"kb/index.json item {position} video {video_id!r} filename must start with "
            f"published date {published_text!r}"
        )

    indexed_source = repo_root / Path(*relative.parts)
    source = indexed_source.resolve()
    collection_root = (repo_root / "kb" / relative.parts[1]).resolve()
    if not is_within(source, collection_root):
        raise ValueError(
            f"kb/index.json item {position} video {video_id!r} path escapes its collection: "
            f"{path_text!r}"
        )
    if source != indexed_source:
        raise ValueError(
            f"kb/index.json item {position} video {video_id!r} path must not traverse symlinks: "
            f"{path_text!r}"
        )
    if not source.is_file():
        raise FileNotFoundError(
            f"kb/index.json item {position} video {video_id!r} file does not exist: {source}"
        )
    return item, video_id, published, source, relative.parts[1]


def validate_destination(
    repo_root: Path, destination: Path, collection: str
) -> None:
    """Require a lexical, symlink-free destination inside its exact collection root."""
    collection_root = repo_root / "kb" / collection
    if collection_root.resolve() != collection_root:
        raise ValueError(
            f"classification destination collection must be the exact lexical root "
            f"{collection_root} and must not traverse symlinks"
        )
    if not is_within(destination, collection_root):
        raise ValueError(f"classification destination escapes its collection: {destination}")
    if destination.resolve() != destination:
        raise ValueError(f"classification destination must not traverse symlinks: {destination}")

    current = repo_root
    for part in destination.relative_to(repo_root).parts:
        current /= part
        if current.is_symlink():
            raise ValueError(
                f"classification destination must not traverse symlinks: {destination}"
            )


def video_move(
    repo_root: Path, item: object, cutoff: dt.date, position: int = 0
) -> Move | None:
    """Validate an indexed video and plan either direction of reclassification."""
    _, _, published, source, collection = validate_video_item(repo_root, item, position)
    expected_collection = "current" if published >= cutoff else "historical"
    if collection == expected_collection:
        return None
    destination = repo_root / "kb" / expected_collection / str(published.year) / source.name
    validate_destination(repo_root, destination, expected_collection)
    return source, destination


def destination_parts(raw_target: str) -> tuple[str, str, bool] | None:
    angled = raw_target.startswith("<") and raw_target.endswith(">")
    target = raw_target[1:-1] if angled else raw_target
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or not parts.path or parts.path.startswith("/"):
        return None
    return unquote(parts.path), urlunsplit(("", "", "", parts.query, parts.fragment)), angled


def rewritten_target(
    raw_target: str,
    old_source: Path,
    new_source: Path,
    moves: dict[Path, Path],
    repo_root: Path,
) -> str:
    parsed = destination_parts(raw_target)
    if not parsed:
        return raw_target
    raw_path, suffix, angled = parsed
    old_target = (old_source.parent / raw_path).resolve()
    if not is_within(old_target, repo_root):
        return raw_target
    new_target = moves.get(old_target, old_target)
    if old_source == new_source and new_target == old_target:
        return raw_target
    relative = Path(os.path.relpath(new_target, new_source.parent)).as_posix()
    encoded = quote(relative, safe="/@:-._~!$&'*+,;=") + suffix
    return f"<{encoded}>" if angled else encoded


def _is_escaped(text: str, position: int) -> bool:
    backslashes = 0
    position -= 1
    while position >= 0 and text[position] == "\\":
        backslashes += 1
        position -= 1
    return backslashes % 2 == 1


def _label_end(text: str, opening: int) -> int | None:
    depth = 1
    position = opening + 1
    while position < len(text):
        character = text[position]
        if character in "[]" and not _is_escaped(text, position):
            depth += 1 if character == "[" else -1
            if depth == 0:
                return position
        position += 1
    return None


def rewrite_inline_links(
    text: str,
    old_source: Path,
    new_source: Path,
    moves: dict[Path, Path],
    repo_root: Path,
) -> str:
    """Rewrite inline link targets, including links with nested label brackets."""
    pieces: list[str] = []
    copied_until = 0
    search_from = 0
    while True:
        opening = text.find("[", search_from)
        if opening < 0:
            pieces.append(text[copied_until:])
            break
        if _is_escaped(text, opening):
            search_from = opening + 1
            continue
        closing = _label_end(text, opening)
        if closing is None or closing + 1 >= len(text) or text[closing + 1] != "(":
            search_from = opening + 1
            continue

        target_start = closing + 2
        while target_start < len(text) and text[target_start] in " \t":
            target_start += 1
        if target_start >= len(text):
            search_from = opening + 1
            continue
        if text[target_start] == "<":
            target_end = text.find(">", target_start + 1)
            if target_end < 0 or "\n" in text[target_start:target_end]:
                search_from = opening + 1
                continue
            target_end += 1
        else:
            target_end = target_start
            while target_end < len(text) and text[target_end] not in " \t\r\n)":
                target_end += 1
        if target_end == target_start:
            search_from = opening + 1
            continue

        pieces.append(text[copied_until:target_start])
        pieces.append(
            rewritten_target(
                text[target_start:target_end], old_source, new_source, moves, repo_root
            )
        )
        copied_until = target_end
        search_from = target_end
    return "".join(pieces)


def rewrite_links_in_text(
    text: str,
    old_source: Path,
    new_source: Path,
    moves: dict[Path, Path],
    repo_root: Path,
) -> str:
    def replace(match: re.Match[str]) -> str:
        target = rewritten_target(match["target"], old_source, new_source, moves, repo_root)
        return match["prefix"] + target

    text = rewrite_inline_links(text, old_source, new_source, moves, repo_root)
    return REFERENCE_LINK_RE.sub(replace, text)


def rewrite_non_code_line(
    line: str,
    old_source: Path,
    new_source: Path,
    moves: dict[Path, Path],
    repo_root: Path,
) -> str:
    pieces: list[str] = []
    position = 0
    while True:
        opening = re.search(r"`+", line[position:])
        if not opening:
            pieces.append(rewrite_links_in_text(line[position:], old_source, new_source, moves, repo_root))
            break
        start = position + opening.start()
        delimiter = opening.group(0)
        pieces.append(rewrite_links_in_text(line[position:start], old_source, new_source, moves, repo_root))
        end = line.find(delimiter, start + len(delimiter))
        if end < 0:
            pieces.append(line[start:])
            break
        end += len(delimiter)
        pieces.append(line[start:end])
        position = end
    return "".join(pieces)


def rewrite_markdown(
    text: str,
    old_source: Path,
    new_source: Path,
    moves: dict[Path, Path],
    repo_root: Path,
) -> str:
    output: list[str] = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        match = FENCE_RE.match(line)
        if fence is None:
            if match:
                marker = match["fence"]
                fence = marker[0], len(marker)
                output.append(line)
            else:
                output.append(rewrite_non_code_line(line, old_source, new_source, moves, repo_root))
            continue

        if match:
            marker = match["fence"]
            if (
                marker[0] == fence[0]
                and len(marker) >= fence[1]
                and not match["rest"].strip()
            ):
                fence = None
        output.append(line)
    return "".join(output)


def atomic_write(path: Path, content: str) -> None:
    mode = path.stat().st_mode
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    )
    temporary = Path(handle.name)
    try:
        try:
            handle.write(content)
        finally:
            handle.close()
        temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _snapshot(path: Path) -> FileSnapshot:
    return path.read_bytes(), path.stat().st_mode


def _restore(path: Path, snapshot: FileSnapshot) -> None:
    content, mode = snapshot
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False)
    temporary = Path(handle.name)
    try:
        try:
            handle.write(content)
        finally:
            handle.close()
        temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _validate_index_path(index_path: Path) -> None:
    if index_path.is_symlink():
        raise ValueError("kb/index.json must be a regular file, not a symlink")
    if not index_path.is_file():
        raise FileNotFoundError(f"kb/index.json is not a regular file: {index_path}")


def _new_directories(path: Path, stop: Path) -> list[Path]:
    directories: list[Path] = []
    current = path
    while current != stop and not current.exists():
        directories.append(current)
        current = current.parent
    if current.exists() and not current.is_dir():
        raise NotADirectoryError(f"classification destination parent is not a directory: {current}")
    return directories


def _rollback(
    moves: list[Move],
    markdown_changes: dict[Path, tuple[Path, str]],
    snapshots: dict[Path, FileSnapshot],
    index_path: Path,
    index_snapshot: FileSnapshot,
    created_directories: list[Path],
) -> None:
    errors: list[Exception] = []
    attempted_sources = {source for source, _ in moves}
    for old_source, (new_source, _) in markdown_changes.items():
        if old_source in attempted_sources and new_source.exists():
            current = new_source
        elif old_source.exists():
            current = old_source
        else:
            current = new_source if new_source != old_source else old_source
        try:
            _restore(current, snapshots[old_source])
        except Exception as error:  # pragma: no cover - only a second filesystem failure
            errors.append(error)
    try:
        _restore(index_path, index_snapshot)
    except Exception as error:  # pragma: no cover - only a second filesystem failure
        errors.append(error)

    for source, destination in reversed(moves):
        try:
            if destination.exists() and source.exists():
                destination.unlink()
            elif destination.exists():
                source.parent.mkdir(parents=True, exist_ok=True)
                os.replace(destination, source)
        except Exception as error:  # pragma: no cover - only a second filesystem failure
            errors.append(error)
    for directory in sorted(set(created_directories), key=lambda path: len(path.parts), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    if errors:
        raise RuntimeError("classification failed and rollback was incomplete") from errors[0]


def classify(repo_root: Path, today: dt.date) -> int:
    repo_root = repo_root.resolve()
    for collection in ("current", "historical"):
        collection_root = repo_root / "kb" / collection
        validate_destination(repo_root, collection_root, collection)
    index_path = repo_root / "kb" / "index.json"
    _validate_index_path(index_path)
    index_snapshot = _snapshot(index_path)
    try:
        items: object = json.loads(index_snapshot[0])
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"kb/index.json is not valid UTF-8 JSON: {error}") from error
    if not isinstance(items, list):
        raise ValueError("kb/index.json must contain a JSON list")

    cutoff = trailing_year_cutoff(today)
    moves_by_source: dict[Path, Path] = {}
    destination_sources: dict[Path, Path] = {}
    source_positions: dict[Path, int] = {}
    moved_items: list[tuple[int, Path]] = []
    validated_items: list[dict[str, Any]] = []
    video_positions: dict[str, int] = {}
    previous_published: dt.date | None = None

    for position, raw_item in enumerate(items):
        item, video_id, published, source, collection = validate_video_item(
            repo_root, raw_item, position
        )
        if previous_published is not None and published > previous_published:
            raise ValueError(
                f"kb/index.json items must be ordered newest first; item {position} "
                f"published {published.isoformat()} follows {previous_published.isoformat()}"
            )
        previous_published = published
        if video_id in video_positions:
            raise ValueError(
                f"kb/index.json items {video_positions[video_id]} and {position} use duplicate "
                f"video_id {video_id!r}"
            )
        video_positions[video_id] = position
        if source in source_positions:
            raise ValueError(
                f"kb/index.json items {source_positions[source]} and {position} use duplicate path: {source}"
            )
        source_positions[source] = position
        validated_items.append(item)
        expected_collection = "current" if published >= cutoff else "historical"
        if collection == expected_collection:
            continue
        move_source = source
        destination = repo_root / "kb" / expected_collection / str(published.year) / source.name
        validate_destination(repo_root, destination, expected_collection)
        if destination in destination_sources:
            raise ValueError(
                f"duplicate classification destination for items "
                f"{source_positions[destination_sources[destination]]} and {position}: {destination}"
            )
        moves_by_source[move_source] = destination
        destination_sources[destination] = move_source
        moved_items.append((position, destination))

    if not moves_by_source:
        return 0

    for source, destination in moves_by_source.items():
        if destination.exists():
            raise FileExistsError(
                f"classification destination already exists for indexed file {source}: {destination}"
            )
        _new_directories(destination.parent, repo_root)

    markdown_changes: dict[Path, tuple[Path, str]] = {}
    snapshots: dict[Path, FileSnapshot] = {}
    for source in repo_root.rglob("*.md"):
        if source.is_symlink() or ".git" in source.parts:
            continue
        old_source = source.resolve()
        new_source = moves_by_source.get(old_source, old_source)
        original = source.read_text(encoding="utf-8")
        rewritten = rewrite_markdown(original, old_source, new_source, moves_by_source, repo_root)
        if rewritten != original or old_source != new_source:
            markdown_changes[old_source] = new_source, rewritten
            snapshots[old_source] = _snapshot(old_source)

    updated_items = [dict(item) for item in validated_items]
    for position, destination in moved_items:
        updated_items[position]["path"] = destination.relative_to(repo_root).as_posix()
    updated_index = json.dumps(updated_items, indent=2, ensure_ascii=False) + "\n"

    moves = list(moves_by_source.items())
    _validate_index_path(index_path)
    attempted_moves: list[Move] = []
    created_directories: list[Path] = []
    try:
        for _, destination in moves:
            collection = destination.relative_to(repo_root / "kb").parts[0]
            validate_destination(repo_root, destination, collection)
            missing = _new_directories(destination.parent, repo_root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            created_directories.extend(missing)
        for source, destination in moves:
            collection = destination.relative_to(repo_root / "kb").parts[0]
            validate_destination(repo_root, destination, collection)
            if destination.exists():
                raise FileExistsError(
                    f"classification destination already exists for indexed file "
                    f"{source}: {destination}"
                )
            attempted_moves.append((source, destination))
            source.rename(destination)
        for _, (new_source, content) in markdown_changes.items():
            atomic_write(new_source, content)
        _validate_index_path(index_path)
        atomic_write(index_path, updated_index)
    except BaseException:
        _rollback(
            attempted_moves,
            markdown_changes,
            snapshots,
            index_path,
            index_snapshot,
            created_directories,
        )
        raise
    return len(moves)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--today", help="execution date for deterministic runs (YYYY-MM-DD)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    except ValueError as error:
        raise SystemExit(f"invalid --today date: {error}") from error
    moved = classify(args.repo_root, today)
    print(f"Reclassified {moved} video{'s' if moved != 1 else ''}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
