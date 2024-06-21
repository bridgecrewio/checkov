from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.report import Report
from checkov.common.util.type_forcers import force_dict
from checkov.gitlab_ci.checks.registry import registry
from checkov.gitlab_ci.common.resource_id_utils import generate_resource_key_recursive
from checkov.runner_filter import RunnerFilter
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from collections.abc import Iterable


class Runner(YamlRunner):
    check_type = CheckType.GITLAB_CI  # noqa: CCE003  # a static attribute

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    @staticmethod
    def _parse_file(
        f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if Runner.is_workflow_file(f):
            return YamlRunner._parse_file(f=f, file_content=file_content)

        return None

    @staticmethod
    def is_workflow_file(file_path: str) -> bool:
        """
        :return: True if the file mentioned is in the gitlab workflow name .gitlab-ci.yml. Otherwise: False
        """
        return file_path.endswith((".gitlab-ci.yml", ".gitlab-ci.yaml"))

    def included_paths(self) -> Iterable[str]:
        return (".gitlab-ci.yml", ".gitlab-ci.yaml")

    def get_resource(self, file_path: str, key: str, supported_entities: Iterable[str],
                     start_line: int = -1, end_line: int = -1, graph_resource: bool = False) -> str:
        file_config = force_dict(self.definitions[file_path])
        if not file_config:
            return key
        resource_id: str = generate_resource_key_recursive(conf=file_config, key='', start_line=start_line,
                                                           end_line=end_line)
        return resource_id

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
