from __future__ import annotations

import re
from pathlib import Path
from typing import cast

from typing_extensions import Literal

from checkov.bicep.checks.param.registry import registry as param_registry
from checkov.bicep.checks.resource.registry import registry as resource_registry
from checkov.bicep.parser import Parser
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import CheckType, Report
from checkov.common.runners.base_runner import BaseRunner
from checkov.common.typing import _CheckResult
from checkov.runner_filter import RunnerFilter


class Runner(BaseRunner):
    check_type = CheckType.BICEP
    bicep_cli = "bicep"

    block_type_registries: dict[Literal["parameters", "resources"], BaseCheckRegistry] = {
        "parameters": param_registry,
        "resources": resource_registry,
    }

    def run(
        self,
        root_folder: str | Path,
        external_checks_dir: list[str] | None = None,
        files: list[str] | None = None,
        runner_filter: RunnerFilter = RunnerFilter(),
        collect_skip_comments: bool = True,
    ) -> Report:
        report = Report(Runner.check_type)

        file_paths: set[Path] = set()
        if root_folder:
            root_path = Path(root_folder)
            file_paths = {file_path for file_path in root_path.rglob("*.bicep")}
        if files:
            for file in files:
                if file.endswith(".bicep"):
                    file_paths.add(Path(file))


        definitions, definitions_raw = Parser().get_files_definitions(file_paths)

        for file_path, definition in definitions.items():
            for block_type, registry in Runner.block_type_registries.items():
                block_type_confs = definition.get(block_type)
                if block_type_confs:
                    for name, conf in block_type_confs.items():
                        results = registry.scan(
                            scanned_file=str(file_path),
                            entity={name: conf},
                            skipped_checks=[],
                            runner_filter=runner_filter,
                        )

                        if results:
                            file_code_lines = definitions_raw[file_path]
                            start_line = cast(int, conf["__start_line__"])  # it is alwasy set for the main block types
                            end_line = cast(int, conf["__end_line__"])  # it is alwasy set for the main block types

                            cleaned_path = self.clean_file_path(file_path)
                            resource_id = f"{conf['type']}.{name}"
                            report.add_resource(f"{cleaned_path}:{resource_id}")

                            suppressions = self.search_for_suppression(code_lines=file_code_lines[start_line - 1 : end_line])

                            for check, check_result in results.items():
                                if check.id in suppressions.keys():
                                    check_result = suppressions[check.id]
                                elif check.bc_id and check.bc_id in suppressions.keys():
                                    check_result = suppressions[check.bc_id]

                                record = Record(
                                    check_id=check.id,
                                    bc_check_id=check.bc_id,
                                    check_name=check.name,
                                    check_result=check_result,
                                    code_block=file_code_lines[start_line - 1 : end_line],
                                    file_path=str(cleaned_path),
                                    file_line_range=[start_line, end_line],
                                    resource=resource_id,
                                    check_class=check.__class__.__module__,
                                    file_abs_path=str(file_path.absolute()),
                                    evaluations=None,
                                )
                                record.set_guideline(check.guideline)
                                report.add_record(record=record)

        return report

    def search_for_suppression(self, code_lines: list[tuple[int, str]]) -> dict[str, _CheckResult]:
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

    def clean_file_path(self, file_path: Path) -> Path:
        path_parts = [part for part in file_path.parts if part not in (".", "..")]

        return Path(*path_parts)
