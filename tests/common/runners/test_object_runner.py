from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.runners.object_runner import Runner
from checkov.runner_filter import RunnerFilter

SAMPLE_DIR = Path(__file__).parent / "sample_dir"


# Since ObjectRunner is an abstract class, we can't instantiate it.
# This class is used only for testing by filling up the abstract implementations.
class ObjectRunnerImplementedAbstractions(Runner):
    def _parse_file(
            self, f: str
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        return None

    def get_start_end_lines(self, end: int, result_config: dict[str, Any], start: int) -> tuple[int, int]:
        return 1, 1

    def import_registry(self) -> BaseCheckRegistry:
        return BaseCheckRegistry("")

    def require_external_checks(self) -> bool:
        return False


def test_run_loads_all_walked_files_in_one_call() -> None:
    # given
    runner = ObjectRunnerImplementedAbstractions()
    expected_files = {str(path) for path in SAMPLE_DIR.rglob("*") if path.is_file()}

    # when
    with patch.object(runner, "_load_files") as load_files:
        runner.run(root_folder=str(SAMPLE_DIR))

    # then
    load_files.assert_called_once()
    assert set(load_files.call_args.kwargs["files_to_load"]) == expected_files


def test_run_loads_all_walked_files_in_one_call_with_excluded_paths() -> None:
    # given
    runner = ObjectRunnerImplementedAbstractions()
    expected_files = {
        str(path)
        for path in SAMPLE_DIR.rglob("*")
        if path.is_file() and "dir33" not in path.relative_to(SAMPLE_DIR).parts
    }

    # when
    with patch.object(runner, "_load_files") as load_files:
        runner.run(root_folder=str(SAMPLE_DIR), runner_filter=RunnerFilter(excluded_paths=["dir33"]))

    # then
    load_files.assert_called_once()
    files_to_load = load_files.call_args.kwargs["files_to_load"]
    assert set(files_to_load) == expected_files
    assert not any(f"{os.sep}dir33{os.sep}" in file for file in files_to_load)
