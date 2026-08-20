from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import cleanup  # noqa: E402
import collect  # noqa: E402


class ExistingVideoIdsTests(unittest.TestCase):
    def test_uses_only_central_index(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "kb" / "videos" / "index.json"
            legacy.parent.mkdir(parents=True)
            legacy.write_text(json.dumps([{"video_id": "legacy"}]))
            self.assertEqual(collect.existing_video_ids(root), set())

            primary = root / "kb" / "index.json"
            primary.write_text(json.dumps([{"video_id": "primary"}]))
            self.assertEqual(collect.existing_video_ids(root), {"primary"})


class CleanVttTests(unittest.TestCase):
    def test_cleans_ordinary_mm_ss_and_hh_mm_ss_cues(self) -> None:
        content = """WEBVTT

1
00:01 --> 00:03
Hello <i>ordinary</i> captions.

2
01:02:03.400 --> 01:02:05.000
They keep working.
"""
        self.assertEqual(
            collect.clean_vtt(content),
            "[00:00:01] Hello ordinary captions. They keep working.",
        )

    def test_preserves_genuine_repetition_and_stutters_in_ordinary_cues(self) -> None:
        content = """WEBVTT

00:00:00.000 --> 00:00:01.000
go

00:00:01.000 --> 00:00:02.000
go now

00:00:02.000 --> 00:00:03.000
I I think so.
"""
        self.assertEqual(collect.clean_vtt(content), "[00:00:00] go go now I I think so.")

    def test_preserves_repetition_in_ordinary_cue_after_rolling_cue(self) -> None:
        content = """WEBVTT

00:00:00.000 --> 00:00:01.000
go<00:00:00.500><c> now</c>

00:00:01.000 --> 00:00:02.000
now please

00:00:02.000 --> 00:00:03.000
go now
"""
        self.assertEqual(
            collect.clean_vtt(content),
            "[00:00:00] go now now please go now",
        )

    def test_parses_youtube_whitespace_and_cumulative_snapshot_cues(self) -> None:
        content = """WEBVTT
Kind: captions
Language: en

00:00:00.240 --> 00:00:02.710 align:start position:0%
\x20
This<00:00:00.640><c> is</c><00:00:00.880><c> Blake</c><00:00:01.439><c> and</c><00:00:01.680><c> this</c><00:00:01.839><c> is</c><00:00:02.000><c> Zach.</c><00:00:02.560><c> And</c>

00:00:02.710 --> 00:00:02.720 align:start position:0%
This is Blake and this is Zach. And
\x20

00:00:02.720 --> 00:00:04.390 align:start position:0%
This is Blake and this is Zach. And
together<00:00:03.040><c> with</c><00:00:03.280><c> two</c><00:00:03.520><c> more</c><00:00:03.760><c> of</c><00:00:03.840><c> their</c><00:00:04.080><c> friends,</c>

00:00:04.390 --> 00:00:04.400 align:start position:0%
together with two more of their friends,
\x20

00:00:04.400 --> 00:00:05.990 align:start position:0%
together with two more of their friends,
they<00:00:04.640><c> built</c><00:00:04.880><c> one</c><00:00:05.040><c> of</c><00:00:05.120><c> the</c><00:00:05.279><c> most</c><00:00:05.440><c> successful</c>
"""
        self.assertEqual(
            collect.clean_vtt(content),
            (
                "[00:00:00] This is Blake and this is Zach. And together with two more "
                "of their friends, they built one of the most successful"
            ),
        )

    def test_preserves_new_timed_repetition_after_rolling_history(self) -> None:
        content = """WEBVTT

00:00:00.000 --> 00:00:01.000
go

00:00:01.000 --> 00:00:03.000
go
go<00:00:02.000><c> now</c>
"""
        self.assertEqual(collect.clean_vtt(content), "[00:00:00] go go now")

    def test_preserves_repeated_speech_in_untimed_youtube_emission_lines(self) -> None:
        content = """WEBVTT

00:00:00.000 --> 00:00:02.000
Cali<00:00:01.000><c> Cali.</c>

00:00:02.000 --> 00:00:02.010
Cali Cali.

00:00:02.010 --> 00:00:03.000
Cali Cali.
Cali.

00:00:03.000 --> 00:00:03.010
Cali.

00:00:03.010 --> 00:00:04.000
Cali.
Cali.
"""
        self.assertEqual(collect.clean_vtt(content), "[00:00:00] Cali Cali. Cali. Cali.")


class CaptionSelectionTests(unittest.TestCase):
    def test_prefers_creator_vtt_in_any_english_locale(self) -> None:
        info = {
            "subtitles": {
                "en": [{"ext": "json3", "url": "manual-json"}],
                "en-GB": [{"ext": "vtt", "url": "manual-vtt"}],
            },
            "automatic_captions": {"en": [{"ext": "vtt", "url": "auto-vtt"}]},
        }
        self.assertEqual(
            collect.choose_caption(info),
            ("manual-vtt", "YouTube creator captions (en-GB)"),
        )

    def test_selects_only_vtt(self) -> None:
        info = {
            "subtitles": {"en-US": [{"ext": "srv3", "url": "manual"}]},
            "automatic_captions": {"en-orig": [{"ext": "json3", "url": "auto"}]},
        }
        self.assertIsNone(collect.choose_caption(info))

    def test_orders_all_creator_tracks_before_automatic_tracks(self) -> None:
        info = {
            "subtitles": {
                "en-GB": [{"ext": "vtt", "url": "creator-gb"}],
                "en": [
                    {"ext": "vtt", "url": "creator-en-1"},
                    {"ext": "vtt", "url": "creator-en-2"},
                ],
            },
            "automatic_captions": {"en": [{"ext": "vtt", "url": "automatic"}]},
        }
        self.assertEqual(
            [url for url, _ in collect.caption_candidates(info)],
            ["creator-en-1", "creator-en-2", "creator-gb", "automatic"],
        )

    @patch.object(collect, "download_text", side_effect=[OSError("failed"), "WEBVTT\n"])
    def test_falls_back_after_download_failure(self, download_text) -> None:
        info = {
            "subtitles": {"en": [{"ext": "vtt", "url": "broken"}]},
            "automatic_captions": {"en": [{"ext": "vtt", "url": "empty"}]},
        }
        transcript, source = collect.retrieve_caption(info)
        self.assertEqual(transcript, "")
        self.assertIn("download failed", source or "")
        self.assertEqual([call.args[0] for call in download_text.call_args_list], ["broken", "empty"])

    @patch.object(
        collect,
        "download_text",
        side_effect=[
            "WEBVTT\n",
            "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nAutomatic works.\n",
        ],
    )
    def test_falls_back_after_empty_cleanup(self, download_text) -> None:
        info = {
            "subtitles": {"en": [{"ext": "vtt", "url": "empty"}]},
            "automatic_captions": {"en": [{"ext": "vtt", "url": "automatic"}]},
        }
        self.assertEqual(
            collect.retrieve_caption(info),
            ("[00:00:00] Automatic works.", "YouTube automatic captions (en)"),
        )
        self.assertEqual([call.args[0] for call in download_text.call_args_list], ["empty", "automatic"])


class UrlExtractionTests(unittest.TestCase):
    def test_preserves_balanced_delimiters_and_strips_external_punctuation(self) -> None:
        urls = collect.extract_urls(
            "See https://example.com/wiki/Thing_(concept)). Then "
            "https://example.com/list[item]."
        )
        self.assertEqual(urls[0], "https://example.com/wiki/Thing_(concept)")
        self.assertEqual(urls[1], "https://example.com/list[item]")

    def test_retains_duplicate_original_occurrences(self) -> None:
        urls = collect.extract_urls("https://example.com/a https://www.example.com/a/ https://example.com/a")
        self.assertEqual(
            urls[:3],
            ["https://example.com/a", "https://www.example.com/a/", "https://example.com/a"],
        )

    def test_keeps_exact_match_separate_and_preserves_terminal_bang_and_star(self) -> None:
        occurrences = collect.extract_url_occurrences(
            "See https://example.com/wiki/Thing_(concept)). "
            "https://example.com/bang! https://example.com/star*"
        )
        self.assertEqual(
            occurrences[:3],
            [
                {
                    "original_url": "https://example.com/wiki/Thing_(concept)).",
                    "url": "https://example.com/wiki/Thing_(concept)",
                },
                {"original_url": "https://example.com/bang!", "url": "https://example.com/bang!"},
                {"original_url": "https://example.com/star*", "url": "https://example.com/star*"},
            ],
        )


class PublicUrlSafetyTests(unittest.TestCase):
    def test_rejects_non_public_literal_addresses_before_opening(self) -> None:
        unsafe = (
            "http://127.0.0.1/",
            "http://10.0.0.1/",
            "http://169.254.169.254/latest/meta-data/",
            "http://224.0.0.1/",
            "http://192.0.2.1/",
            "http://0.0.0.0/",
        )
        for url in unsafe:
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, "non-public"):
                collect.validate_public_http_url(url)

    def test_rejects_credentials_local_names_and_disallowed_ports(self) -> None:
        unsafe = (
            "https://user:secret@example.com/",
            "http://localhost/",
            "http://service.local/",
            "https://example.com:8443/",
            "http://example.com:0/",
            "https://example.com:0/",
            "http://example.com:00/",
        )
        for url in unsafe:
            with self.subTest(url=url), self.assertRaises(ValueError):
                collect.validate_public_http_url(url)

    @patch.object(collect, "build_opener")
    def test_fetch_rejects_private_target_before_initial_request(self, build_opener) -> None:
        result = collect.fetch_link("http://127.0.0.1/secret")
        build_opener.assert_not_called()
        self.assertIn("non-public", result["error"])

    def test_redirect_handler_rejects_redirect_to_private(self) -> None:
        handler = collect.PublicRedirectHandler()
        with self.assertRaisesRegex(ValueError, "non-public"):
            handler.redirect_request(
                MagicMock(), MagicMock(), 302, "Found", MagicMock(), "http://127.0.0.1/admin"
            )

    @patch.object(
        collect.socket,
        "getaddrinfo",
        return_value=[(2, 1, 6, "", ("10.0.0.8", 443))],
    )
    def test_rejects_hostname_resolving_to_private(self, getaddrinfo) -> None:
        with self.assertRaisesRegex(ValueError, "non-public"):
            collect.validate_public_http_url("https://example.com/")
        getaddrinfo.assert_called_once()

    @patch.object(collect.socket, "socket")
    @patch.object(
        collect,
        "_resolve_public_host",
        return_value=[(2, 1, 6, "", ("93.184.216.34", 80))],
    )
    def test_connection_is_pinned_to_validated_address(self, resolve_public_host, socket_factory) -> None:
        connection = collect._public_http_connection("example.com", timeout=4)
        connection.connect()
        resolve_public_host.assert_called_once_with("example.com", 80)
        socket_factory.return_value.connect.assert_called_once_with(("93.184.216.34", 80))


class FetchLinkTests(unittest.TestCase):
    def test_malformed_request_becomes_bounded_error_evidence(self) -> None:
        result = collect.fetch_link("https://[bad")
        self.assertEqual(result["url"], "https://[bad")
        self.assertIn("ValueError", result["error"])
        self.assertLessEqual(len(result["error"]), collect.MAX_ERROR_CHARS)

    def test_bounded_metadata_ends_at_a_word_boundary(self) -> None:
        self.assertEqual(collect._clean_evidence("one two three", 10), "one two...")

    @patch.object(collect, "_open_public")
    def test_collects_only_bounded_link_metadata(self, open_public) -> None:
        response = MagicMock()
        response.status = 200
        response.url = "https://example.com/final"
        response.read.return_value = (
            b"<html><head><title> Example title </title>"
            b'<meta name="description" content="Short evidence">'
            b"</head><body>Visible body that must not be retained</body></html>"
        )
        open_public.return_value = response

        result = collect.fetch_link("https://example.com/start")

        response.read.assert_called_once_with(collect.MAX_LINK_RESPONSE_BYTES)
        self.assertEqual(
            result,
            {
                "url": "https://example.com/start",
                "status": 200,
                "final_url": "https://example.com/final",
                "title": "Example title",
                "description": "Short evidence",
            },
        )
        self.assertNotIn("body", json.dumps(result))
        self.assertNotIn("page_text", result)


class DiscoverTests(unittest.TestCase):
    @patch.object(collect, "full_metadata")
    @patch.object(collect, "run_json")
    def test_scans_past_known_boundary_and_applies_inclusive_range(
        self, run_json, full_metadata
    ) -> None:
        run_json.return_value = {
            "entries": [
                {"id": "too-new"},
                {"id": "known-new"},
                {"id": "until-boundary"},
                {"id": "known-middle"},
                {"id": "since-boundary"},
                {"id": "too-old"},
                {"id": "never-fetched"},
            ]
        }
        dates = {
            "too-new": "20240201",
            "until-boundary": "20240131",
            "since-boundary": "20240101",
            "too-old": "20231231",
            "never-fetched": "20230101",
        }
        full_metadata.side_effect = lambda video_id: {"id": video_id, "upload_date": dates[video_id]}

        result = collect.discover(
            collect.CHANNEL_URL,
            {"known-new", "known-middle"},
            "20240101",
            "20240131",
        )

        self.assertEqual([item["id"] for item in result], ["until-boundary", "since-boundary"])
        self.assertEqual(
            [call.args[0] for call in full_metadata.call_args_list],
            ["too-new", "until-boundary", "since-boundary", "too-old"],
        )


class MainContractTests(unittest.TestCase):
    def test_collector_and_cleanup_reject_symlinked_artifacts_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            external_workspace = Path(outside) / "starter-story-sync-existing"
            external_workspace.mkdir()
            (external_workspace / "manifest.json").write_text(
                json.dumps(
                    {
                        "collector": collect.COLLECTOR_MARKER,
                        "channel": collect.CHANNEL_URL,
                    }
                )
            )
            (root / "artifacts").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(SystemExit, "symlinked artifacts"):
                collect.create_workspace(root.resolve())
            with self.assertRaisesRegex(SystemExit, "unexpected path"):
                cleanup.cleanup_workspace(root, root / "artifacts" / external_workspace.name)
            self.assertTrue(external_workspace.exists())

    def test_rejects_workspace_not_physically_direct_artifacts_child(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory).resolve()
            external_workspace = Path(outside) / "starter-story-sync-external"
            external_workspace.mkdir()
            with (
                patch.object(collect.tempfile, "mkdtemp", return_value=str(external_workspace)),
                self.assertRaisesRegex(SystemExit, "direct artifacts child"),
            ):
                collect.create_workspace(root)
            self.assertFalse(external_workspace.exists())

    def test_rejects_since_before_2024(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(
                repo_root=Path(directory), since="2023-12-31", until=None
            )
            with patch.object(collect, "parse_args", return_value=args):
                with self.assertRaisesRegex(SystemExit, "on or after 2024-01-01"):
                    collect.main()
            self.assertFalse((Path(directory) / "artifacts").exists())

    def test_rejects_custom_channel_and_workspace_options(self) -> None:
        for option in ("--channel", "--workspace"):
            with (
                self.subTest(option=option),
                patch.object(sys, "argv", ["collect.py", option, "x"]),
                redirect_stderr(io.StringIO()),
            ):
                with self.assertRaises(SystemExit):
                    collect.parse_args()

    @patch.object(
        collect,
        "fetch_link",
        new=MagicMock(side_effect=lambda url: {"url": url, "status": 200}),
    )
    @patch.object(collect, "discover")
    def test_manifest_retains_each_link_occurrence_with_video_id(self, discover) -> None:
        discover.return_value = [
            {
                "id": "video-1",
                "upload_date": "20240101",
                "title": "Title",
                "description": (
                    "https://example.com/path https://www.example.com/path/ "
                    "https://example.com/path"
                ),
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(repo_root=Path(directory), since="2024-01-01", until=None)
            output = io.StringIO()
            with patch.object(collect, "parse_args", return_value=args), redirect_stdout(output):
                self.assertEqual(collect.main(), 0)
            workspace = Path(output.getvalue().splitlines()[0])
            manifest = json.loads((workspace / "manifest.json").read_text())

        self.assertEqual(manifest["collector"], collect.COLLECTOR_MARKER)
        self.assertIsInstance(manifest["links"], list)
        self.assertEqual(
            [item["url"] for item in manifest["links"][:3]],
            [
                "https://example.com/path",
                "https://www.example.com/path/",
                "https://example.com/path",
            ],
        )
        self.assertTrue(all(item["video_id"] == "video-1" for item in manifest["links"]))
        self.assertEqual(
            [item["original_url"] for item in manifest["links"][:3]],
            [
                "https://example.com/path",
                "https://www.example.com/path/",
                "https://example.com/path",
            ],
        )
        self.assertEqual(
            manifest["videos"][0]["description_urls"][:3],
            [
                "https://example.com/path",
                "https://www.example.com/path/",
                "https://example.com/path",
            ],
        )

    @patch.object(
        collect,
        "discover",
        new=MagicMock(side_effect=RuntimeError("collection failed")),
    )
    def test_prints_workspace_then_removes_it_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(repo_root=Path(directory), since="2024-01-01", until=None)
            output = io.StringIO()
            with patch.object(collect, "parse_args", return_value=args), redirect_stdout(output):
                with self.assertRaisesRegex(RuntimeError, "collection failed"):
                    collect.main()
            workspace = Path(output.getvalue().splitlines()[0])
            self.assertFalse(workspace.exists())

    @patch.object(
        collect,
        "discover",
        new=MagicMock(side_effect=RuntimeError("collection failed")),
    )
    def test_surfaces_automatic_workspace_cleanup_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(repo_root=Path(directory), since="2024-01-01", until=None)
            with (
                patch.object(collect, "parse_args", return_value=args),
                patch.object(collect.shutil, "rmtree", side_effect=OSError("cleanup failed")),
                redirect_stdout(io.StringIO()),
                self.assertRaisesRegex(OSError, "cleanup failed") as raised,
            ):
                collect.main()
        self.assertIsInstance(raised.exception.__cause__, RuntimeError)


if __name__ == "__main__":
    unittest.main()
