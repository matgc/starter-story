# Output format

## Video file

Save each new video as `videos/YYYY/YYYY-MM-DD-<title-slug>.md`.

```markdown
---
video_id: "<YouTube ID>"
title: "<title>"
published: YYYY-MM-DD
duration_seconds: <integer>
source: https://www.youtube.com/watch?v=<id>
transcript_source: <caption or transcription source>
---

# <Title>

[Watch on YouTube](<source>)

## Marketing strategy summary

- <target customer and painful problem>
- <primary acquisition channel>
- <specific tactics and evidence>
- <validation or feedback loop>
- <economics and caveat when stated>

### Reusable playbook

1. <specific action>
2. <specific action>
3. <specific action>

## Transcript

> <source and accuracy note>

[00:00:00] <verbatim transcript paragraphs>

## Links mentioned in the description

- [<stable name>](<description URL>) - [local notes](../../links/<canonical-slug>.md)
```

Keep the transcript verbatim apart from caption cleanup. Do not silently correct claims, rewrite speech, or insert analysis into it.

## Link file

Save one file per canonical destination as `links/<canonical-slug>.md`. Reuse it when tracking URLs resolve to the same destination.

```markdown
# <Stable link name>

## What it contains

<One factual paragraph based on the fetched page title, metadata, and visible content. State when the page is inaccessible or gone.>

## Source details

- Canonical destination: [<URL>](<URL>)
- Resolved destination observed during collection: [<URL>](<URL>)
- HTTP status observed: <status>
- Description links that resolve to this page:
  - [<original URL>](<original URL>)

## Mentioned by

- [<Video title>](../videos/YYYY/<video file>.md)
```

## Index updates

1. Add the video to `videos/index.json`, newest first.
2. Add it to `videos/README.md`, newest first.
3. Add its full strategy summary to `strategies/README.md`, newest first.
4. Update `strategies/overview.md` only when the new evidence changes the synthesis.
5. Add new canonical link notes to `links/README.md` in name order.
