#!/usr/bin/env python3
"""Collect metadata, captions, and bounded link evidence for Starter Story videos."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import html
import http.client
import ipaddress
import json
import re
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPHandler,
    HTTPRedirectHandler,
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
)

CHANNEL_URL = "https://www.youtube.com/@starterstory/videos"
EARLIEST_DATE = dt.date(2024, 1, 1)
COLLECTOR_MARKER = "fetch-starter-story"
URL_RE = re.compile(r"https?://[^\s<>]+")
EXTERNAL_TRAILING_PUNCTUATION = ".,;:?>'\""
CLOSING_DELIMITERS = {")": "(", "]": "[", "}": "{"}
ALLOWED_HTTP_PORTS = {80, 443}
LOCAL_HOST_SUFFIXES = (
    ".internal",
    ".invalid",
    ".lan",
    ".local",
    ".localdomain",
    ".localhost",
    ".test",
)
SHARED_DESCRIPTION_LINKS = (
    "https://www.youtube.com/@StarterStoryBuild",
    "https://www.starterstory.com/jobs",
)
MAX_LINK_RESPONSE_BYTES = 256_000
MAX_TITLE_CHARS = 1_000
MAX_DESCRIPTION_CHARS = 4_000
MAX_URL_CHARS = 8_000
MAX_ERROR_CHARS = 1_000
VTT_TIMESTAMP_PATTERN = r"(?:\d+:)?\d{2}:\d{2}(?:[.,]\d+)?"
TIMING_RE = re.compile(
    rf"^\s*({VTT_TIMESTAMP_PATTERN})\s+-->\s+({VTT_TIMESTAMP_PATTERN})(?:\s|$)"
)
INLINE_VTT_TIMESTAMP_RE = re.compile(r"<\d{2}:\d{2}(?::\d{2})?[.,]\d+>")


class MetadataParser(HTMLParser):
    """Extract only bounded title and description metadata from bounded HTML input."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._title_depth = 0
        self._title_parts: list[str] = []
        self.description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "title":
            self._title_depth += 1
            return
        if tag != "meta" or self.description:
            return
        attributes = {name.lower(): value or "" for name, value in attrs}
        kind = (attributes.get("name") or attributes.get("property") or "").lower()
        if kind in {"description", "og:description"}:
            self.description = _clean_evidence(attributes.get("content", ""), MAX_DESCRIPTION_CHARS)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title" and self._title_depth:
            self._title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._title_depth and sum(map(len, self._title_parts)) < MAX_TITLE_CHARS:
            self._title_parts.append(data)

    @property
    def title(self) -> str:
        return _clean_evidence(" ".join(self._title_parts), MAX_TITLE_CHARS)


def _clean_evidence(value: str, limit: int) -> str:
    normalized = re.sub(r"\s+", " ", html.unescape(value)).strip()
    if len(normalized) <= limit:
        return normalized
    if limit <= 3:
        return normalized[:limit]
    cut = normalized[: limit - 3]
    prefix = cut if normalized[len(cut)].isspace() else cut.rsplit(" ", 1)[0]
    prefix = prefix.rstrip(".,;:!?")
    return f"{prefix or cut}..."


def run_json(command: list[str]) -> dict:
    process = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(process.stdout)


def existing_video_ids(repo_root: Path) -> set[str]:
    index = repo_root / "kb" / "index.json"
    if not index.exists():
        return set()
    return {item["video_id"] for item in json.loads(index.read_text()) if item.get("video_id")}


def _normalize_timestamp(timestamp: str) -> str:
    whole = re.split(r"[.,]", timestamp, maxsplit=1)[0]
    parts = whole.split(":")
    if len(parts) == 2:
        parts.insert(0, "0")
    return f"{int(parts[0]):02d}:{int(parts[1]):02d}:{int(parts[2]):02d}"


def _timestamp_seconds(timestamp: str) -> float:
    parts = timestamp.replace(",", ".").split(":")
    if len(parts) == 2:
        parts.insert(0, "0")
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])


def _clean_caption_line(line: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", line)
    cleaned = re.sub(r"^\s*>>\s*", "", html.unescape(cleaned))
    return re.sub(r"\s+", " ", cleaned).strip()


def clean_vtt(content: str) -> str:
    """Convert VTT cues without treating repeated timed speech as caption history."""
    cues: list[tuple[str, float, list[str], list[bool]]] = []
    cue_start: str | None = None
    cue_end: str | None = None
    cue_lines: list[str] = []
    after_payload_blank = False

    def finish_cue() -> None:
        nonlocal cue_start, cue_end, cue_lines, after_payload_blank
        if cue_start is not None and cue_end is not None:
            lines: list[str] = []
            timed: list[bool] = []
            for line in cue_lines:
                cleaned = _clean_caption_line(line)
                if cleaned:
                    lines.append(cleaned)
                    timed.append(bool(INLINE_VTT_TIMESTAMP_RE.search(line)))
            if lines:
                duration = _timestamp_seconds(cue_end) - _timestamp_seconds(cue_start)
                cues.append((_normalize_timestamp(cue_start), duration, lines, timed))
        cue_start = None
        cue_end = None
        cue_lines = []
        after_payload_blank = False

    for line in content.splitlines():
        timing = TIMING_RE.match(line)
        if timing:
            finish_cue()
            cue_start, cue_end = timing.group(1), timing.group(2)
        elif cue_start is not None and not line.strip():
            if cue_lines:
                after_payload_blank = True
        elif cue_start is not None:
            if after_payload_blank:
                finish_cue()
            else:
                cue_lines.append(line)
    finish_cue()

    fragments: list[tuple[str, str]] = []
    snapshots = [
        duration <= 0.05 and len(lines) == 1 and not any(timed)
        for _, duration, lines, timed in cues
    ]
    for index, (timestamp, _, lines, timed) in enumerate(cues):
        previous_lines = cues[index - 1][2] if index else []
        next_lines = cues[index + 1][2] if index + 1 < len(cues) else []
        if snapshots[index] and (
            (previous_lines and previous_lines[-1] == lines[0])
            or (next_lines and next_lines[0] == lines[0])
        ):
            continue

        first_line = 0
        if index and snapshots[index - 1] and lines[0] == previous_lines[-1]:
            first_line = 1
        timed_lines = [line_index for line_index, has_timestamp in enumerate(timed) if has_timestamp]
        if timed_lines:
            first_line = max(first_line, timed_lines[0])

        emitted_lines = lines[first_line:]
        if emitted_lines:
            fragments.append((timestamp, " ".join(emitted_lines)))

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


def _english_languages(tracks: dict) -> list[str]:
    languages = [language for language in tracks if language.lower() == "en" or language.lower().startswith("en-")]
    return sorted(languages, key=lambda language: (language.lower() != "en", language.lower()))


def caption_candidates(info: dict) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    groups = (
        ("creator captions", info.get("subtitles") or {}),
        ("automatic captions", info.get("automatic_captions") or {}),
    )
    for source, tracks in groups:
        for language in _english_languages(tracks):
            candidates.extend(
                (item["url"], f"YouTube {source} ({language})")
                for item in tracks.get(language) or []
                if item.get("ext", "").lower() == "vtt" and item.get("url")
            )
    return candidates


def choose_caption(info: dict) -> tuple[str, str] | None:
    """Return the first candidate for callers that only need preference order."""
    candidates = caption_candidates(info)
    return candidates[0] if candidates else None


def retrieve_caption(info: dict) -> tuple[str, str | None]:
    """Try every English VTT candidate in creator-then-automatic order."""
    failures: list[str] = []
    for caption_url, source in caption_candidates(info):
        try:
            transcript = clean_vtt(download_text(caption_url))
        except Exception as error:
            failures.append(f"{source}: download failed ({type(error).__name__})")
            continue
        if transcript:
            return transcript, source
        failures.append(f"{source}: empty after cleanup")
    if failures:
        return "", "caption candidates exhausted: " + "; ".join(failures)
    return "", None


def _resolve_public_host(hostname: str, port: int) -> list[tuple]:
    hostname = hostname.rstrip(".").casefold()
    try:
        literal_address = ipaddress.ip_address(hostname)
    except ValueError:
        literal_address = None
    if literal_address is None and (
        "." not in hostname or hostname == "localhost" or hostname.endswith(LOCAL_HOST_SUFFIXES)
    ):
        raise ValueError("local host names are not allowed")
    try:
        resolved = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except OSError as error:
        raise ValueError(f"host resolution failed: {error}") from error
    addresses = {ipaddress.ip_address(str(item[4][0]).split("%", 1)[0]) for item in resolved}
    if not addresses or any(
        not address.is_global
        or address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
        for address in addresses
    ):
        raise ValueError("URL host resolves to a non-public address")
    return resolved


def validate_public_http_url(url: str) -> None:
    """Reject URLs that cannot safely target a public HTTP service."""
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must use HTTP(S) and include a host")
    if "@" in parsed.netloc or parsed.username is not None or parsed.password is not None:
        raise ValueError("URL credentials are not allowed")
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("URL has an invalid port") from error
    effective_port = port if port is not None else (443 if parsed.scheme.lower() == "https" else 80)
    if effective_port not in ALLOWED_HTTP_PORTS:
        raise ValueError(f"URL port {effective_port} is not allowed")
    if not parsed.hostname:
        raise ValueError("URL must include a host")
    _resolve_public_host(parsed.hostname, effective_port)


def _connect_public(address, timeout=None, source_address=None):
    """Connect only to the exact public addresses returned by the safety lookup."""
    hostname, port = address
    last_error = None
    for family, socktype, proto, _, socket_address in _resolve_public_host(hostname, port):
        connection = None
        try:
            connection = socket.socket(family, socktype, proto)
            if timeout is not None:
                connection.settimeout(timeout)
            if source_address:
                connection.bind(source_address)
            connection.connect(socket_address)
            return connection
        except OSError as error:
            last_error = error
            if connection is not None:
                connection.close()
    raise last_error or OSError("no public address was available")


def _public_http_connection(*args, **kwargs):
    connection = http.client.HTTPConnection(*args, **kwargs)
    setattr(connection, "_create_connection", _connect_public)
    return connection


def _public_https_connection(*args, **kwargs):
    connection = http.client.HTTPSConnection(*args, **kwargs)
    setattr(connection, "_create_connection", _connect_public)
    return connection


class PublicHTTPHandler(HTTPHandler):
    def http_open(self, request):
        return self.do_open(_public_http_connection, request)


class PublicHTTPSHandler(HTTPSHandler):
    def __init__(self) -> None:
        self.context = ssl.create_default_context()
        super().__init__(context=self.context)

    def https_open(self, request):
        return self.do_open(_public_https_connection, request, context=self.context)


class PublicRedirectHandler(HTTPRedirectHandler):
    """Validate the target before urllib follows any redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_public_http_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _open_public(request: Request, timeout: int):
    validate_public_http_url(request.full_url)
    opener = build_opener(
        ProxyHandler({}),
        PublicHTTPHandler(),
        PublicHTTPSHandler(),
        PublicRedirectHandler(),
    )
    return opener.open(request, timeout=timeout)


def download_text(url: str, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with _open_public(request, timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _strip_external_url_punctuation(url: str) -> str:
    url = url.rstrip(EXTERNAL_TRAILING_PUNCTUATION)
    while url and url[-1] in CLOSING_DELIMITERS:
        closing = url[-1]
        opening = CLOSING_DELIMITERS[closing]
        if url.count(closing) <= url.count(opening):
            break
        url = url[:-1].rstrip(EXTERNAL_TRAILING_PUNCTUATION)
    return url


def extract_url_occurrences(description: str) -> list[dict[str, str]]:
    occurrences = [
        {"original_url": match.group(0), "url": _strip_external_url_punctuation(match.group(0))}
        for match in URL_RE.finditer(description)
    ]
    navigation_urls = {item["url"] for item in occurrences}
    for shared in SHARED_DESCRIPTION_LINKS:
        if shared not in navigation_urls:
            occurrences.append({"original_url": shared, "url": shared})
    return occurrences


def extract_urls(description: str) -> list[str]:
    """Return cleaned navigable URLs while retaining extraction compatibility."""
    return [item["url"] for item in extract_url_occurrences(description)]


def fetch_link(url: str) -> dict:
    """Fetch bounded redirect, status, title, and meta-description evidence only."""
    result: dict = {"url": url}
    response = None
    try:
        request = Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; StarterStoryResearch/1.0)"},
        )
        try:
            response = _open_public(request, 20)
        except HTTPError as error:
            response = error
        result["status"] = response.status
        result["final_url"] = str(response.url)[:MAX_URL_CHARS]
        body = response.read(MAX_LINK_RESPONSE_BYTES).decode("utf-8", errors="replace")
        parser = MetadataParser()
        parser.feed(body)
        parser.close()
        result["title"] = parser.title
        result["description"] = parser.description
    except Exception as error:  # Retain inaccessible links for a local note.
        result["error"] = _clean_evidence(f"{type(error).__name__}: {error}", MAX_ERROR_CHARS)
    finally:
        if response is not None:
            response.close()
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


def discover(channel: str, known: set[str], since: str, until: str | None = None) -> list[dict]:
    """Discover unknown videos in the inclusive date range from newest to oldest."""
    playlist = run_json(["yt-dlp", "--flat-playlist", "--dump-single-json", "--no-warnings", channel])
    entries = [entry for entry in playlist.get("entries", []) if entry and entry.get("id")]
    collected = []
    for entry in entries:
        video_id = entry["id"]
        if video_id in known:
            continue
        info = full_metadata(video_id)
        upload_date = info.get("upload_date") or ""
        if upload_date and upload_date < since:
            break
        if not upload_date or (until and upload_date > until):
            continue
        collected.append(info)
    return collected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--since", default="2024-01-01", help="inclusive start date (YYYY-MM-DD)")
    parser.add_argument("--until", help="inclusive end date (YYYY-MM-DD)")
    return parser.parse_args()


def create_workspace(repo_root: Path) -> Path:
    artifacts = repo_root / "artifacts"
    if artifacts.is_symlink():
        raise SystemExit(f"refusing symlinked artifacts directory: {artifacts}")
    artifacts.mkdir(exist_ok=True)
    if not artifacts.is_dir() or artifacts.is_symlink():
        raise SystemExit(f"artifacts path is not a real directory: {artifacts}")
    resolved_artifacts = artifacts.resolve(strict=True)
    if resolved_artifacts != artifacts:
        raise SystemExit(f"artifacts directory escapes the repository: {artifacts}")

    workspace = Path(tempfile.mkdtemp(prefix="starter-story-sync-", dir=resolved_artifacts))
    if (
        workspace.parent != resolved_artifacts
        or workspace.is_symlink()
        or workspace.resolve(strict=True).parent != resolved_artifacts
    ):
        if not workspace.is_symlink():
            try:
                workspace.rmdir()
            except OSError:
                pass
        raise SystemExit(f"workspace is not a direct artifacts child: {workspace}")
    return workspace


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    try:
        since_date = dt.date.fromisoformat(args.since)
        until_date = dt.date.fromisoformat(args.until) if args.until else None
    except ValueError as error:
        raise SystemExit(f"invalid date: {error}") from error
    if since_date < EARLIEST_DATE:
        raise SystemExit("--since must be on or after 2024-01-01")
    if until_date and until_date < since_date:
        raise SystemExit("--until must be on or after --since")
    since = since_date.strftime("%Y%m%d")
    until = until_date.strftime("%Y%m%d") if until_date else None

    workspace = create_workspace(repo_root)
    try:
        print(workspace, flush=True)
        (workspace / "metadata").mkdir()
        (workspace / "transcripts").mkdir()

        known = existing_video_ids(repo_root)
        discovered = discover(CHANNEL_URL, known, since, until)
        videos = []
        link_occurrences: list[dict] = []
        for info in discovered:
            upload_date = info.get("upload_date") or ""
            if upload_date < since or (until and upload_date > until):
                continue
            video_id = info["id"]
            metadata_path = workspace / "metadata" / f"{video_id}.json"
            metadata_path.write_text(json.dumps(info, indent=2, ensure_ascii=False))
            transcript_path = None
            transcript_status = "needs_audio_transcription"
            transcript, transcript_source = retrieve_caption(info)
            if transcript:
                transcript_path = workspace / "transcripts" / f"{video_id}.txt"
                transcript_path.write_text(transcript + "\n")
                transcript_status = "ready"
            occurrences = extract_url_occurrences(info.get("description") or "")
            urls = [item["url"] for item in occurrences]
            link_occurrences.extend({**item, "video_id": video_id} for item in occurrences)
            videos.append(
                {
                    "video_id": video_id,
                    "title": info.get("title"),
                    "upload_date": upload_date,
                    "duration": info.get("duration"),
                    "source": info.get("webpage_url")
                    or f"https://www.youtube.com/watch?v={video_id}",
                    "metadata_path": str(metadata_path.relative_to(workspace)),
                    "transcript_path": (
                        str(transcript_path.relative_to(workspace)) if transcript_path else None
                    ),
                    "transcript_source": transcript_source,
                    "transcript_status": transcript_status,
                    "description_urls": urls,
                }
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            fetched = list(pool.map(fetch_link, [item["url"] for item in link_occurrences]))
        for occurrence, fetched_item in zip(link_occurrences, fetched):
            occurrence.update({key: value for key, value in fetched_item.items() if key != "url"})

        manifest = {
            "collector": COLLECTOR_MARKER,
            "collected_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "channel": CHANNEL_URL,
            "since": args.since,
            "until": args.until,
            "video_count": len(videos),
            "videos": videos,
            "links": link_occurrences,
        }
        (workspace / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        )
        print(f"Collected {len(videos)} new videos; manifest: {workspace / 'manifest.json'}")
    except BaseException as collection_error:
        try:
            shutil.rmtree(workspace)
        except BaseException as cleanup_error:
            raise cleanup_error from collection_error
        raise
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileNotFoundError as error:
        print(f"Missing required executable: {error.filename}", file=sys.stderr)
        raise SystemExit(2)
