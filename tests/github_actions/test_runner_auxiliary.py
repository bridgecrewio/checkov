from __future__ import annotations
from typing import Any

from checkov.common.checks.base_check_registry import BaseCheckRegistry

from checkov.common.runners.object_runner import Runner


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


def test_get_jobs() -> None:
    string_step_definition = {
        "name": "String step",
        "jobs": {
            "install-dbx": {
                "name": "Install dependencies and project in dev mode",
                "steps": {
                    "run": "pip install dbx\n",
                    "__startline__": 185,
                    "__endline__": 188
                },
                "__startline__": 183,
                "__endline__": 188
            },
            "__startline__": 29,
            "__endline__": 346
        },
        "__startline__": 1,
        "__endline__": 346
    }

    end_line_to_job_name_dict = ObjectRunnerImplementedAbstractions()._get_jobs(string_step_definition)

    assert end_line_to_job_name_dict[188] == "install-dbx"
