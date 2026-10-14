from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from checkov.azure_pipelines.checks.registry import registry
from checkov.azure_pipelines.common.resource_id_utils import generate_resource_key_recursive
from checkov.common.output.report import CheckType, Report
from checkov.runner_filter import RunnerFilter
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from collections.abc import Iterable


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
        """Check if file is an Azure Pipelines workflow file.

        Supports both standard and custom file locations including
        .azuredevops/, pipelines/ folders, and any yaml file explicitly
        passed via --file flag for azure_pipelines framework.

        Args:
            file_path: Path to candidate pipeline file.

        Returns:
            True if file should be treated as Azure Pipelines config.
        """
        if not file_path:
            return False
        lower = file_path.lower().replace("\\", "/")
        # Standard naming always counts
        if lower.endswith(("azure-pipelines.yml", "azure-pipelines.yaml")):
            return True
        # Custom locations from issue 7525: .azuredevops/, pipelines/, or any
        # filename containing pipeline or azure, ending in yaml/yml
        if lower.endswith((".yml", ".yaml")):
            if ".azuredevops/" in lower or "pipelines/" in lower:
                return True
            if "pipeline" in lower or "azure" in lower:
                return True
            # If user explicitly passes file via --file, Runner is invoked
            # with files list already filtered to azure_pipelines framework.
            # So any yaml file selected for this framework should scan.
            # Allow any .yml/.yaml to support fully custom names like ci.yml
            return True
        return False

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
