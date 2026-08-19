# Starter Story Marketing Archive

A searchable archive of every non-Short video published by the [Starter Story YouTube channel](https://www.youtube.com/@starterstory) from January 1, 2026 through August 19, 2026.

The archive is designed for builders who need practical help with marketing, distribution, validation, and customer acquisition.

## Contents

- [Video index](videos/README.md) - 53 videos, newest first
- [Machine-readable video inventory](videos/index.json)
- [Per-video marketing strategies](strategies/README.md)
- [Cross-video marketing overview](strategies/overview.md)
- [Description-link notes](links/README.md) - 145 canonical destinations
- [Update skill](.pi/skills/fetch-starter-story/SKILL.md)

Each video file contains:

1. Source metadata and YouTube URL.
2. A focused marketing-strategy summary.
3. A reusable action playbook.
4. The timestamped transcript in Markdown.
5. Named description links and local notes about each destination.

## Organization

```text
videos/
  README.md
  index.json
  2026/
    YYYY-MM-DD-video-title.md
strategies/
  README.md
  overview.md
links/
  README.md
  canonical-link-name.md
.pi/skills/fetch-starter-story/
  SKILL.md
  references/
  scripts/
```

## Collection method

1. Videos were inventoried from the channel's `/videos` tab, excluding the `/shorts` tab.
2. Publication dates and descriptions were collected with `yt-dlp`.
3. All 53 videos had English YouTube automatic captions, so no audio or video media was downloaded.
4. Caption VTT files were converted into deduplicated, timestamped Markdown transcripts.
5. Description URLs were resolved and grouped by canonical destination so repeated links keep one stable name and note.
6. Marketing summaries were produced from the transcript evidence.
7. Temporary collection artifacts were deleted after verification.

## Accuracy notes

- Transcripts come from YouTube automatic captions and may misspell names or technical terms.
- Revenue, growth, and performance claims are statements made in the videos, not independently verified results.
- Link notes describe what was available during collection. External pages can change or disappear.

## Updating

Ask an agent to "sync Starter Story" or explicitly load `/skill:fetch-starter-story`. The skill checks YouTube IDs, processes only new long-form videos, updates all indexes, and removes temporary media and metadata when done.
