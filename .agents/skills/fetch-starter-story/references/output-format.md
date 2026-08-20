# Output format

Read this reference before writing sync output. Repository-relative paths and JSON keys below are the contract.

## Collection and path rules

1. Store each video at `kb/<collection>/YYYY/YYYY-MM-DD-<title-slug>.md`.
2. Compute `<collection>` from the execution date's trailing-12-calendar-month cutoff:
   - `published >= cutoff`: `current` (the boundary stays current);
   - `published < cutoff`: `historical`.
3. Use the video's publication year for `YYYY`. Never change `published` during classification.
4. Keep every video, current and historical, in central `kb/index.json`; do not create per-collection JSON indexes.
5. The collector always creates a direct `artifacts/starter-story-sync-*` child, prints it immediately, and attempts to remove it automatically on failure. It surfaces any failed automatic cleanup. It accepts no custom channel or workspace.
6. The collector rejects dates before 2024-01-01 and reads known YouTube IDs only from `kb/index.json`.

## Collection manifest

`manifest.json` has the collector marker `"collector": "fetch-starter-story"`. Its `links` value is a list with one record for every original URL occurrence. Each record keeps exact extraction attribution in `original_url`, the separately cleaned navigable `url`, `video_id`, and only bounded redirect, HTTP status, title, meta-description, or error evidence. Valid terminal URL characters such as `!` and `*` remain in the navigable URL. Normalized variants and repeated occurrences remain separate. Each video's `description_urls` contains navigable URLs. The collector never stores response bodies, visible page text, or general page content in the manifest. When a destination cannot be reached, `final_url` and `status` are optional; use the retained error evidence instead of inventing observations.

## Video file

Use this template:

```markdown
---
video_id: "<YouTube ID>"
title: "<title>"
published: YYYY-MM-DD
duration_seconds: <integer>
source: https://www.youtube.com/watch?v=<id>
transcript_source: <caption or audio-transcription source>
---

# <Title>

[Watch on YouTube](<source>)

## Marketing strategy summary

- <target customer and painful problem>
- <primary acquisition channel>
- <specific distribution tactics and evidence>
- <validation or feedback loop>
- <monetization evidence and caveat when stated>

### Reusable playbook

1. <specific action>
2. <specific action>
3. <specific action>

## Transcript

> <source and accuracy note>

[00:00:00] <verbatim transcript paragraphs>

## Links mentioned in the description

- [<stable name>](<original description URL>) - [local notes](../../links/<video-or-channel>/<canonical-slug>.md)
```

Keep the transcript verbatim apart from caption cleanup. Do not silently correct claims, rewrite speech, or insert analysis into it.

## Link placement and eligibility

1. Save one canonical note in `kb/links/video/<canonical-slug>.md` for a founder or video-specific destination.
2. Save one canonical note in `kb/links/channel/<canonical-slug>.md` for recurring Starter Story, sponsor, promotion, course, program, database, or other channel-wide destinations.
3. Reuse the existing note path and exact stable name when `kb/links/index.json` already has the canonical destination, even if another URL redirects to it.
4. Never retrieve or archive the contents of changing databases, courses, programs, or channel resources. Their notes contain only observed URL-resolution metadata, title/status evidence, and direct video associations.
5. Optionally save `kb/links/archives/<canonical-slug>.md` only for a public, accessible, static historical article/post whose content directly supplies marketing information. Archiving is best effort. Omit `archive_path` when the source is ineligible or inaccessible.
6. Preserve inaccessible, blocked, and removed observations. Describe no content that was not retrieved.

## Link note

Use this template in `video/` or `channel/`:

```markdown
# <Stable link name>

## What it contains

<One factual paragraph from allowed evidence, or an explicit inaccessible/blocked/removed statement.>

## Source details

- Scope: <video|channel>
- Canonical destination: [<canonical URL>](<canonical URL>)
- Resolved destination observed: <[resolved URL](resolved URL)|not resolved>
- Access status observed: <HTTP status|inaccessible|blocked|removed|not observed>
- Content policy: <metadata only|eligible static article archived>
- Archived static copy: <[local archive](../archives/<canonical-slug>.md)|none>
- Description URLs resolving here:
  - [<original URL>](<original URL>)

## Mentioned by

- [<Video title>](../../<current-or-historical>/YYYY/<video-file>.md)
```

For canonical reuse, merge original URLs and `Mentioned by` entries without renaming the note. Retain the observed access status and error when no page is available. A resolved destination and HTTP status are optional for inaccessible links; write `not resolved` and `not observed` rather than inventing them.

## Static article/post archive

Use only after all eligibility checks pass:

```markdown
---
canonical_url: "<canonical URL>"
source_title: "<article/post title>"
source_published: <YYYY-MM-DD|unknown>
retrieved_at: "<ISO-8601 timestamp>"
---

# <Article/post title>

> Best-effort static snapshot of a public historical article/post, retained because it directly documents marketing information. Navigation, forms, comments, and unrelated page chrome are omitted.

## Marketing relevance

<Why this source is directly relevant to acquisition, distribution, validation, positioning, or monetization.>

## Archived article/post

<Cleaned source text. Preserve claims as published; do not add analysis.>

## Source note

[<Stable link name>](../<video-or-channel>/<canonical-slug>.md)
```

Do not create this file for profiles, home pages, applications, live feeds, changing resources, channel resources, inaccessible pages, databases, courses, or programs.

## Central video index

Keep `kb/index.json` as a JSON list, newest first. Use this exact entry shape:

```json
[
  {
    "video_id": "abc123",
    "published": "2025-08-20",
    "title": "Example title",
    "source": "https://www.youtube.com/watch?v=abc123",
    "path": "kb/current/2025/2025-08-20-example-title.md"
  }
]
```

Every video appears exactly once. The `path` is authoritative for current/historical classification without opening video content.

## Link index and direct associations

Keep `kb/links/index.json` with both canonical records and direct per-video lookup:

```json
{
  "links": [
    {
      "name": "Example article",
      "canonical_url": "https://example.com/growth-post",
      "note_path": "kb/links/video/example-article.md",
      "archive_path": "kb/links/archives/example-article.md",
      "scope": "video",
      "video_ids": ["abc123"]
    }
  ],
  "by_video": {
    "abc123": [
      {
        "name": "Example article",
        "canonical_url": "https://example.com/growth-post",
        "note_path": "kb/links/video/example-article.md",
        "archive_path": "kb/links/archives/example-article.md",
        "scope": "video"
      }
    ]
  }
}
```

Omit `archive_path` in both locations when no eligible archive exists. Each `by_video` list directly represents every description-link association for that YouTube ID, including reused canonical notes and inaccessible destinations.

## Human indexes and strategy synthesis

1. Update root `README.md` counts, date range, classification date, and directory layout.
2. Update `kb/README.md` with separate current and historical sections, newest first, and paths matching `kb/index.json`.
3. Update `kb/strategies/README.md` with each new video's full strategy summary, newest first.
4. Update `kb/strategies/overview.md` only when evidence changes the cross-video synthesis.
5. Update `kb/links/README.md` with separate channel, video, and eligible static-archive sections. Sort notes by stable name and omit the archive section when empty.

## Final consistency checks

1. Parse both JSON indexes and confirm their shapes.
2. Match each `kb/index.json` entry to one existing video file, frontmatter ID/date, collection, and publication year.
3. Match every link record, optional archive, `video_ids` value, and `by_video` association in both directions.
4. Resolve every relative Markdown target. Confirm no duplicate IDs, canonical URLs, note paths, archive paths, or orphan files.
5. Confirm every manifest description URL has one canonical note and direct association, including inaccessible URLs.
6. Confirm no archived content exists for changing databases, courses, programs, or channel resources.
7. Confirm transcripts are non-empty and no audio, video, caption, metadata, or sync workspace remains.
