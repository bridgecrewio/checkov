from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from checkov.common.output.report import CheckType
from checkov.yaml_doc.runner import Runner as YamlRunner

# Import of the checks registry for a specific resource type
from checkov.argo_workflows.checks.registry import registry as template_registry

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Runner(YamlRunner):
    check_type = CheckType.ARGO_WORKFLOWS  # noqa: CCE003

    block_type_registries = {  # noqa: CCE003
        "template": template_registry,
    }

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return self.block_type_registries["template"]

    def _parse_file(
        self, f: str
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if not f.endswith((".yaml", ",yml")):
            return None

        content = Path(f).read_text()
        if "apiVersion" in content and "argoproj.io/" in content:
            return super()._parse_file(f)

        return None
