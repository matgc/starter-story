#!/usr/bin/env python3
"""Collect metadata, captions, and description-link metadata for new Starter Story videos."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

URL_RE = re.compile(r"https?://[^\s<>]+")
TRAILING_URL_PUNCTUATION = ".,;:!?)]}>'\"*"
SHARED_DESCRIPTION_LINKS = (
    "https://www.youtube.com/@StarterStoryBuild",
    "https://www.starterstory.com/jobs",
)


def run_json(command: list[str]) -> dict:
    process = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(process.stdout)


def existing_video_ids(repo_root: Path) -> set[str]:
    index = repo_root / "videos" / "index.json"
    if not index.exists():
        return set()
    return {item["video_id"] for item in json.loads(index.read_text())}


def clean_vtt(content: str) -> str:
    fragments: list[tuple[str, str]] = []
    current_time = "00:00:00"
    for line in content.splitlines():
        timing = re.match(r"(\d\d:\d\d:\d\d)\.\d+ -->", line)
        if timing:
            current_time = timing.group(1)
            continue
        # YouTube's rolling VTT repeats untimed lines. Timed lines contain only new words.
        if "<00:" not in line:
            continue
        cleaned = re.sub(r"<[^>]+>", "", line)
        cleaned = html.unescape(cleaned).replace(">> ", "")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if cleaned:
            fragments.append((current_time, cleaned))

    paragraphs: list[tuple[str, str]] = []
    paragraph: list[str] = []
    start = "00:00:00"
    for timestamp, fragment in fragments:
        if not paragraph:
            start = timestamp
        paragraph.append(fragment)
        length = sum(len(part) for part in paragraph)
        ends_sentence = bool(re.search(r"[.!?][\"']?$", fragment))
        if length >= 550 or (length >= 350 and ends_sentence):
            paragraphs.append((start, " ".join(paragraph)))
            paragraph = []
    if paragraph:
        paragraphs.append((start, " ".join(paragraph)))
    return "\n\n".join(f"[{stamp}] {text}" for stamp, text in paragraphs)


def choose_caption(info: dict) -> tuple[str, str] | None:
    candidates = (
        ("manual captions", info.get("subtitles") or {}, ("en", "en-US", "en-orig")),
        ("automatic captions", info.get("automatic_captions") or {}, ("en-orig", "en", "en-US")),
    )
    for source, tracks, languages in candidates:
        for language in languages:
            formats = tracks.get(language) or []
            preferred = next((item for item in formats if item.get("ext") == "vtt"), None)
            selected = preferred or (formats[0] if formats else None)
            if selected and selected.get("url"):
                return selected["url"], f"YouTube {source} ({language})"
    return None


def download_text(url: str, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def extract_urls(description: str) -> list[str]:
    urls = [match.group(0).rstrip(TRAILING_URL_PUNCTUATION) for match in URL_RE.finditer(description)]
    for shared in SHARED_DESCRIPTION_LINKS:
        if shared not in urls:
            urls.append(shared)
    return urls


def normalize_original(url: str) -> str:
    parts = urlsplit(url)
    host = parts.netloc.lower().removeprefix("www.")
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), host, path, parts.query, ""))


def fetch_link(url: str) -> dict:
    result: dict = {"url": url}
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; StarterStoryResearch/1.0)"},
    )
    try:
        try:
            response = urlopen(request, timeout=20)
        except HTTPError as error:
            response = error
        content_type = response.headers.get("content-type", "")
        body = response.read(2_000_000).decode("utf-8", errors="replace") if "text" in content_type else ""
        result.update(
            status=response.status,
            final_url=response.url,
            content_type=content_type,
        )
        title = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
        descriptions = (
            re.search(
                r'<meta[^>]+(?:name|property)=["\'](?:description|og:description)["\'][^>]+content=["\'](.*?)["\']',
                body,
                re.I | re.S,
            ),
            re.search(
                r'<meta[^>]+content=["\'](.*?)["\'][^>]+(?:name|property)=["\'](?:description|og:description)["\']',
                body,
                re.I | re.S,
            ),
        )
        description = next((match for match in descriptions if match), None)
        result["title"] = html.unescape(re.sub(r"\s+", " ", title.group(1))).strip() if title else ""
        result["description"] = (
            html.unescape(re.sub(r"\s+", " ", description.group(1))).strip() if description else ""
        )
    except Exception as error:  # The manifest must retain inaccessible links for a local note.
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def full_metadata(video_id: str) -> dict:
    return run_json(
        [
            "yt-dlp",
            "--skip-download",
            "--dump-single-json",
            "--no-warnings",
            f"https://www.youtube.com/watch?v={video_id}",
        ]
    )


def discover(channel: str, known: set[str], since: str) -> list[dict]:
    playlist = run_json(["yt-dlp", "--flat-playlist", "--dump-single-json", "--no-warnings", channel])
    entries = [entry for entry in playlist.get("entries", []) if entry and entry.get("id")]
    if known:
        known_positions = [index for index, entry in enumerate(entries) if entry["id"] in known]
        boundary = max(known_positions) if known_positions else len(entries) - 1
        candidates = [entry for entry in entries[: boundary + 1] if entry["id"] not in known]
        return [full_metadata(entry["id"]) for entry in candidates]

    collected = []
    for entry in entries:
        info = full_metadata(entry["id"])
        upload_date = info.get("upload_date") or ""
        if upload_date and upload_date < since:
            break
        collected.append(info)
    return collected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--channel", default="https://www.youtube.com/@starterstory/videos")
    parser.add_argument("--since", default="2026-01-01")
    parser.add_argument("--workspace", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    since = args.since.replace("-", "")
    artifacts = repo_root / "artifacts"
    artifacts.mkdir(exist_ok=True)
    if args.workspace:
        workspace = args.workspace.resolve()
        workspace.mkdir(parents=True, exist_ok=False)
    else:
        workspace = Path(tempfile.mkdtemp(prefix="starter-story-sync-", dir=artifacts))
    (workspace / "metadata").mkdir()
    (workspace / "transcripts").mkdir()

    known = existing_video_ids(repo_root)
    discovered = discover(args.channel, known, since)
    videos = []
    link_occurrences: dict[str, dict] = {}
    for info in discovered:
        upload_date = info.get("upload_date") or ""
        if upload_date < since:
            continue
        video_id = info["id"]
        metadata_path = workspace / "metadata" / f"{video_id}.json"
        metadata_path.write_text(json.dumps(info, indent=2, ensure_ascii=False))
        caption = choose_caption(info)
        transcript_path = None
        transcript_source = None
        transcript_status = "needs_audio_transcription"
        if caption:
            caption_url, transcript_source = caption
            try:
                transcript = clean_vtt(download_text(caption_url))
            except Exception as error:
                transcript_source = f"caption download failed: {type(error).__name__}: {error}"
                transcript = ""
            if transcript:
                transcript_path = workspace / "transcripts" / f"{video_id}.txt"
                transcript_path.write_text(transcript + "\n")
                transcript_status = "ready"
        urls = extract_urls(info.get("description") or "")
        for url in urls:
            key = normalize_original(url)
            link_occurrences.setdefault(key, {"url": url, "video_ids": []})["video_ids"].append(video_id)
        videos.append(
            {
                "video_id": video_id,
                "title": info.get("title"),
                "upload_date": upload_date,
                "duration": info.get("duration"),
                "source": info.get("webpage_url") or f"https://www.youtube.com/watch?v={video_id}",
                "metadata_path": str(metadata_path.relative_to(workspace)),
                "transcript_path": str(transcript_path.relative_to(workspace)) if transcript_path else None,
                "transcript_source": transcript_source,
                "transcript_status": transcript_status,
                "description_urls": urls,
            }
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        fetched = list(pool.map(fetch_link, [item["url"] for item in link_occurrences.values()]))
    for occurrence, fetched_item in zip(link_occurrences.values(), fetched):
        occurrence.update(fetched_item)

    manifest = {
        "collected_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "channel": args.channel,
        "since": args.since,
        "video_count": len(videos),
        "videos": videos,
        "links": link_occurrences,
    }
    (workspace / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(workspace)
    print(f"Collected {len(videos)} new videos; manifest: {workspace / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileNotFoundError as error:
        print(f"Missing required executable: {error.filename}", file=sys.stderr)
        raise SystemExit(2)
