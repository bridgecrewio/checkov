from __future__ import annotations

import logging
import os
from typing import Any

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.pulumi.parser import parse_pulumi_file
from checkov.pulumi.translator import translate_resources
from checkov.runner_filter import RunnerFilter
from checkov.terraform.plan_runner import Runner as TerraformPlanRunner
from checkov.terraform.plan_utils import build_definitions_context

FILE_EXTENSIONS = (".json", ".jsonl", ".ndjson")


def _is_regular_file_in(file_path: str, real_root: str) -> bool:
    """Symlinks can point to files outside of the scanned directory or to devices"""

    real_path = os.path.realpath(file_path)
    try:
        return os.path.isfile(real_path) and os.path.commonpath((real_path, real_root)) == real_root
    except ValueError:
        # different drives on Windows
        return False


class Runner(TerraformPlanRunner):
    """Scans Pulumi previews and stack exports with the Terraform checks

    Resources of the Terraform bridged providers (aws, gcp, azure) are translated to Terraform plan resources.
    """

    check_type = CheckType.PULUMI  # noqa: CCE003  # a static attribute

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # event logs can also be saved as JSON lines
        self.file_extensions = list(FILE_EXTENSIONS)

    def _parse_definitions(
        self,
        root_folder: str | None,
        files: list[str] | None,
        runner_filter: RunnerFilter,
        parsing_errors: dict[str, str],
    ) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        file_paths = list(files or [])
        if root_folder:
            real_root = os.path.realpath(root_folder)
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, runner_filter.excluded_paths)
                filter_ignored_paths(root, f_names, runner_filter.excluded_paths)
                for file in f_names:
                    file_path = os.path.join(root, file)
                    if file.endswith(FILE_EXTENSIONS) and _is_regular_file_in(file_path, real_root):
                        file_paths.append(file_path)

        definitions: dict[str, dict[str, Any]] = {}
        definitions_raw: dict[str, list[tuple[int, str]]] = {}
        for file_path in sorted({os.path.abspath(file) for file in file_paths if file.endswith(FILE_EXTENSIONS)}):
            resources, file_lines = parse_pulumi_file(file_path, parsing_errors)
            if not resources or not file_lines:
                continue
            try:
                definition = translate_resources(resources)
            except Exception as e:
                logging.debug(f"[pulumi] failed to translate file {file_path}", exc_info=True)
                parsing_errors[file_path] = str(e)
                continue
            if not definition["resource"]:
                logging.debug(f"[pulumi] no supported resources found in {file_path}")
                continue
            definitions[file_path] = definition
            definitions_raw[file_path] = file_lines

        return definitions, build_definitions_context(definitions, definitions_raw)

    @property
    def _should_run_deep_analysis(self) -> bool:
        # deep analysis enriches the results with a Terraform configuration
        return False
