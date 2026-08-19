---
name: fetch-starter-story
description: >
  Fetch and archive new long-form Starter Story YouTube videos with transcripts,
  description-link notes, and marketing-strategy summaries. Use this skill when the
  user says "sync Starter Story", "fetch new Starter Story videos", "update the
  transcript archive", "check @starterstory for new videos", or asks to refresh this
  repository from the channel.
---

# Fetch Starter Story

Run this task skill only when the user explicitly asks to fetch or sync videos. It writes repository files and temporarily downloads public metadata or captions.

## Requirements

1. Run from the repository root.
2. Require `python3` and `yt-dlp` on `PATH`.
3. Read `references/output-format.md` before writing final files. It defines the repository contract.

## Collect

Run:

```bash
python3 .pi/skills/fetch-starter-story/scripts/collect.py --repo-root .
```

The command prints a temporary workspace under `artifacts/`. Read its `manifest.json`. Stop when `video_count` is zero, then clean the workspace.

The collector uses the channel's `/videos` tab, which excludes Shorts. It compares YouTube IDs with `videos/index.json`, downloads no video media, prefers English creator captions, and otherwise uses English automatic captions.

## Process new videos

1. Verify each video's publication date is on or after 2026-01-01 and its ID is absent from `videos/index.json`.
2. Verify the item came from `/videos`, not `/shorts`.
3. Use sub-agents for transcript analysis in small batches. This preserves the main agent's context.
4. Write one file per video using the video template.
5. Summarize only marketing evidence in the transcript:
   1. target customer and problem;
   2. acquisition channel;
   3. concrete distribution tactics;
   4. validation and feedback loop;
   5. monetization evidence and caveats;
   6. a reusable action sequence.
6. Keep captions as the transcript. Fix VTT duplication and formatting only; do not rewrite spoken content.

## Caption fallback

When `transcript_status` is `needs_audio_transcription`:

1. Download audio only into the printed workspace. Never store it elsewhere in the repository.
2. Delegate each transcription-only job to a sub-agent using the cheapest available OpenAI model that reliably accepts and transcribes audio. Keep the current model and thinking settings for all non-transcription work.
3. Treat the AI result as a transcript, not a summary. Preserve wording and mark uncertain passages.
4. Delete the audio as soon as its transcript is verified.

Example audio command:

```bash
yt-dlp -x --audio-format mp3 -o '<workspace>/audio/%(id)s.%(ext)s' 'https://www.youtube.com/watch?v=<id>'
```

## Process links

1. Include every explicit description URL plus the rendered `@StarterStoryBuild` channel and `starterstory.com/jobs` links.
2. Resolve redirects. Canonicalize by final host and path while removing tracking queries.
3. Reuse an existing link file and exact display name when the canonical destination already exists.
4. Otherwise create one link file using fetched title, metadata, and visible content.
5. State when a page is inaccessible, blocked, or removed. Do not guess its contents.
6. Add every named link at the end of each related transcript.

## Update and verify

1. Update all indexes listed in the output-format reference.
2. Check that every manifest video has exactly one transcript file and one strategy summary.
3. Check that every description URL has a local link note and every local note target exists.
4. Check for duplicate video IDs, duplicate canonical link files, broken relative links, empty transcripts, and remaining audio/video files.
5. Run repository diagnostics on every changed file and resolve all findings.
6. Clean the exact workspace printed by the collector:

```bash
python3 .pi/skills/fetch-starter-story/scripts/cleanup.py '<workspace>'
```

7. Verify `artifacts/` contains no audio, video, caption, metadata, or temporary sync files.

## Example

Input: `Sync Starter Story and add anything published since the last run.`

Output: new `videos/YYYY/*.md` transcripts, reused or new `links/*.md` notes, updated video/link/strategy indexes, no retained media, and a concise count of added videos and links.

## Do and don't

- Do preserve YouTube IDs as the deduplication key.
- Do use page evidence and transcript evidence for summaries.
- Do keep repeated canonical links under one stable name.
- Don't treat a Short as a long-form video.
- Don't download media when captions are available.
- Don't leave `artifacts/` or speculative link descriptions behind.
