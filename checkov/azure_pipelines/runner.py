from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Any, Optional

from checkov.azure_pipelines.checks.registry import registry
from checkov.azure_pipelines.common.resource_id_utils import generate_resource_key_recursive
from checkov.common.output.report import CheckType, Report
from checkov.runner_filter import RunnerFilter
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from collections.abc import Iterable


# File-name suffixes that the runner recognizes as Azure Pipelines configs out
# of the box. Supplemental suffixes can be supplied via the
# CHECKOV_AZURE_PIPELINES_FILE_NAMES environment variable as a comma- or
# whitespace-separated list (e.g. "ci.yml,pr-pipeline.yaml" or
# ".azuredevops/pr-pipeline.yaml").
DEFAULT_AZURE_PIPELINES_FILE_NAMES: tuple[str, ...] = (
    'azure-pipelines.yml',
    'azure-pipelines.yaml',
)


def _extra_pipelines_file_names() -> tuple[str, ...]:
    raw = os.environ.get('CHECKOV_AZURE_PIPELINES_FILE_NAMES')
    if not raw:
        return ()
    return tuple(part.strip() for part in re.split(r'[,\s]+', raw) if part.strip())


class Runner(YamlRunner):
    check_type = CheckType.AZURE_PIPELINES  # noqa: CCE003  # a static attribute

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    @staticmethod
    def _parse_file(
        f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if Runner.is_workflow_file(f):
            return YamlRunner._parse_file(f=f)
        return None

    @staticmethod
    def is_workflow_file(file_path: str) -> bool:
        suffixes = DEFAULT_AZURE_PIPELINES_FILE_NAMES + _extra_pipelines_file_names()
        return file_path.endswith(suffixes)

    def get_resource(self, file_path: str, key: str, supported_entities: Iterable[str],
                     start_line: int = -1, end_line: int = -1, graph_resource: bool = False) -> str:
        if not self.definitions or not isinstance(self.definitions, dict):
            return key
        resource_name: Optional[str] = generate_resource_key_recursive(start_line, end_line, self.definitions[file_path])
        return resource_name if resource_name else key

    def run(
            self,
            root_folder: str | None = None,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True,
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        report = super().run(root_folder=root_folder, external_checks_dir=external_checks_dir,
                             files=files, runner_filter=runner_filter, collect_skip_comments=collect_skip_comments)
        return report
