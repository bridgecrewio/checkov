from __future__ import annotations

import re
from pathlib import Path

from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.models.enums import CheckResult
from checkov.common.typing import _CheckResult


def get_scannable_file_paths(root_folder: str | Path | None = None, files: list[str] | None = None) -> set[Path]:
    """Finds Bicep files"""

    file_paths: set[Path] = set()

    if root_folder:
        root_path = Path(root_folder)
        file_paths = {file_path for file_path in root_path.rglob("*.bicep")}
    if files:
        for file in files:
            if file.endswith(".bicep"):
                file_paths.add(Path(file))

    return file_paths


def clean_file_path(file_path: Path) -> Path:
    path_parts = [part for part in file_path.parts if part not in (".", "..")]

    return Path(*path_parts)


def search_for_suppression(code_lines: list[tuple[int, str]]) -> dict[str, _CheckResult]:
    """Searches for suppressions in a config block"""

    suppressions = {}

    for _, line in code_lines:
        skip_search = re.search(COMMENT_REGEX, line)
        if skip_search:
            check_result: _CheckResult = {
                "result": CheckResult.SKIPPED,
                "suppress_comment": skip_search.group(3)[1:] if skip_search.group(3) else "No comment provided",
            }
            suppressions[skip_search.group(2)] = check_result

    return suppressions
