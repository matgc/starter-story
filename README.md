# Starter Story Marketing Archive

A searchable archive of 157 non-Short videos published by the [Starter Story YouTube channel](https://www.youtube.com/@starterstory) from January 1, 2024 through August 16, 2026. The current/historical classification is as of August 20, 2026.

The archive is designed for builders who need practical help with marketing, distribution, validation, and customer acquisition.

## Contents

- [Knowledge-base and video index](kb/README.md) - 157 videos, newest first
- [Machine-readable video inventory](kb/index.json)
- [Per-video marketing strategies](kb/strategies/README.md) - 157 evidence-preserving entries
- [Cross-video marketing overview](kb/strategies/overview.md)
- [Description-link notes](kb/links/README.md) - 372 canonical destinations split by channel and video scope
- [Machine-readable link associations](kb/links/index.json)
- [Update skill](.agents/skills/fetch-starter-story/SKILL.md)

Each video file contains source metadata, a marketing-strategy summary, a reusable playbook, the timestamped transcript, and the description links. Local notes are available for the canonical destinations covered by the link index.

## Organization

```text
kb/
  README.md
  index.json
  current/
    2025/
    2026/
  historical/
    2024/
    2025/
  strategies/
    README.md
    overview.md
  links/
    README.md
    index.json
    channel/
    video/
.agents/skills/fetch-starter-story/
  SKILL.md
  references/
  scripts/
```

`current/` is the trailing 12-month window from August 20, 2025 through August 20, 2026, with the boundary included. It contains 92 videos: 53 from 2026 and 39 from 2025. `historical/` contains the 65 older videos: 32 from 2025 and 33 from 2024.

## Collection method

1. Videos were inventoried from the channel's `/videos` tab, excluding Shorts.
2. Publication metadata and descriptions were collected with `yt-dlp`; metadata is retained in video frontmatter and description URLs are retained in each video's footer and the link index.
3. All 157 videos use English YouTube automatic captions; no audio or video media is stored in the repository.
4. Caption VTT files were converted into deduplicated, timestamped Markdown transcripts.
5. Marketing summaries and reusable playbooks were produced from transcript evidence, then copied into the repository-wide strategy index.
6. Description URLs were canonicalized and grouped so repeated destinations keep one stable note; inaccessible or timed-out pages retain explicit status instead of guessed content.
7. The video inventory was regenerated from all frontmatter, sorted newest first, and validated for counts, unique IDs, dates, paths, and local links.
8. Temporary collection artifacts are excluded from the archive after verification.

## Accuracy notes

- Transcripts come from YouTube automatic captions and may misspell names or technical terms.
- Revenue, growth, and performance claims are statements made in the videos, not independently verified results.
- Historical videos provide context; their tactics are not automatically current in 2026.
- Link notes describe what was available during collection. External pages can change or disappear.

## Updating

Ask an agent to "sync Starter Story" or explicitly load `/skill:fetch-starter-story`. Recompute the trailing-12-month boundary during each refresh, preserve frontmatter publication dates, and reclassify videos when they fall outside the current window.
