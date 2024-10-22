from __future__ import annotations

from typing import Any, TYPE_CHECKING

from checkov.bitbucket_pipelines.registry import registry
from checkov.common.bridgecrew.check_type import CheckType
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Runner(YamlRunner):
    check_type = CheckType.BITBUCKET_PIPELINES  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__()

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    @staticmethod
    def is_workflow_file(file_path: str) -> bool:
        """
        :return: True if the file mentioned is named bitbucket-pipelines.yml. Otherwise: False
        """
        return file_path.endswith(("bitbucket-pipelines.yml", "bitbucket-pipelines.yaml"))

    @staticmethod
    def _parse_file(
        f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if Runner.is_workflow_file(f):
            return YamlRunner._parse_file(f)

        return None
