"""Regression tests for download_repos.py.

These cover the timeout handling added for issue #28, plus the existing
BadZipFile and happy-path behaviour of download_and_extract_zip.

Run with:  python3 -m unittest test_download_repos
(no third-party test runner required; uses only the stdlib + requests.)
"""

import io
import os
import tempfile
import unittest
import zipfile
from unittest import mock

import requests

import download_repos


def _make_zip_bytes(entries):
    """Build an in-memory zip archive from a {path: content} mapping."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for path, content in entries.items():
            zf.writestr(path, content)
    return buf.getvalue()


class _FakeResponse:
    def __init__(self, status_code=200, content=b""):
        self.status_code = status_code
        self.content = content


class DownloadAndExtractZipTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base_dir = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def test_happy_path_extracts_and_renames(self):
        """A valid zip is extracted and a -master suffix is stripped."""
        zip_bytes = _make_zip_bytes(
            {"myrepo-master/README.md": "hello", "myrepo-master/sub/file.txt": "x"}
        )
        with mock.patch.object(
            download_repos.requests,
            "get",
            return_value=_FakeResponse(200, zip_bytes),
        ) as mock_get:
            download_repos.download_and_extract_zip(
                "https://example.com/repo.zip", base_dir=self.base_dir
            )

        # requests.get must be called with an explicit timeout (issue #28).
        _, kwargs = mock_get.call_args
        self.assertIn("timeout", kwargs)
        self.assertEqual(kwargs["timeout"], download_repos.REQUEST_TIMEOUT)

        renamed = os.path.join(self.base_dir, "repos", "myrepo")
        self.assertTrue(os.path.isdir(renamed), "directory should be renamed to drop -master")
        self.assertTrue(os.path.isfile(os.path.join(renamed, "README.md")))
        self.assertTrue(os.path.isfile(os.path.join(renamed, "sub", "file.txt")))

    def test_bad_zip_is_handled(self):
        """Garbage content (not a zip) is caught and does not raise."""
        with mock.patch.object(
            download_repos.requests,
            "get",
            return_value=_FakeResponse(200, b"not a zip file"),
        ):
            # Should return cleanly rather than propagating BadZipFile.
            download_repos.download_and_extract_zip(
                "https://example.com/repo.zip", base_dir=self.base_dir
            )

        repo_dir = os.path.join(self.base_dir, "repos")
        # The repos dir is created but nothing was extracted into it.
        self.assertTrue(os.path.isdir(repo_dir))
        self.assertEqual(os.listdir(repo_dir), [])

    def test_non_200_status_does_not_raise(self):
        """A non-200 response is reported but does not crash."""
        with mock.patch.object(
            download_repos.requests,
            "get",
            return_value=_FakeResponse(404, b""),
        ):
            download_repos.download_and_extract_zip(
                "https://example.com/repo.zip", base_dir=self.base_dir
            )


class MainTimeoutHandlingTests(unittest.TestCase):
    """main() must survive a timeout / network error without crashing."""

    def _run_main_with(self, side_effect, config):
        m = mock.mock_open(read_data="ignored")
        with mock.patch.object(download_repos.os.path, "exists", return_value=True), \
             mock.patch("builtins.open", m), \
             mock.patch.object(download_repos.json, "load", return_value=config), \
             mock.patch.object(download_repos.requests, "get", side_effect=side_effect):
            download_repos.main()

    def test_main_handles_timeout(self):
        self._run_main_with(
            requests.Timeout("timed out"),
            [{"url": "https://example.com/repo.zip"}],
        )

    def test_main_handles_request_exception(self):
        self._run_main_with(
            requests.ConnectionError("connection refused"),
            [{"url": "https://example.com/repo.zip"}],
        )


if __name__ == "__main__":
    unittest.main()
