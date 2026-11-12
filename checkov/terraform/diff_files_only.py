"""Diff-files-only scanning: in-memory repository file index for the runner.

INTERNAL switch (CHECKOV_DIFF_FILES_ONLY=true), set only by checkov.terraform.diff_scan.scan.diff_scan (the
`--diff-baseline` CLI path) after it has filled `repository_files`. Do not set it on its own: a regular scan with it set
reads files from an empty index and fails (FileNotFoundError / missing context).

A PR scan in this mode never touches unchanged repository files: the files the runner needs after the graph is built
(existence checks, code lines for record code blocks and checkov:skip comments) are served from an in-memory index that
the caller fills from the baseline artifact plus the changed files. When the flag is off, nothing here is used.
"""
from __future__ import annotations

import os

DIFF_FILES_ONLY_ENV = "CHECKOV_DIFF_FILES_ONLY"


def diff_files_only_enabled() -> bool:
    return os.getenv(DIFF_FILES_ONLY_ENV, "false").lower() == "true"


class RepositoryFileIndex:
    def __init__(self) -> None:
        self._lines_by_path: dict[str, list[str]] = {}

    def set_files(self, lines_by_path: dict[str, list[str]]) -> None:
        self._lines_by_path = dict(lines_by_path)

    def exists(self, path: str) -> bool:
        return path in self._lines_by_path

    def read_lines(self, path: str) -> list[str]:
        if path not in self._lines_by_path:
            raise FileNotFoundError(f"not in the diff-files-only repository index: {path}")
        return self._lines_by_path[path]


repository_files = RepositoryFileIndex()
