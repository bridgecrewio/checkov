from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from checkov.common.bridgecrew.check_type import CheckType

# Import of the checks registry for a specific resource type
from checkov.example_runner.checks.job_registry import registry as job_registry

# Import of the IaC runner to inherit most of the code from
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry


# Inherit either that YamlRunner or the JSONRunner or ObjectRunner
# depending on IaC type or for the latter if a totally new IaC type
class Runner(YamlRunner):
    # EDIT: change below to CheckType.**MY_TYPE**
    # MY_TYPE is defined in report.py in checkov/common/output
    # class CheckType:
    # ...
    #   MY_TYPE = "my_type"
    #
    check_type = CheckType.MY_TYPE  # type:ignore[attr-defined]  # noqa: CCE003  # a static attribute

    # Define your block type
    block_type_registries = {  # noqa: CCE003  # a static attribute
        "jobs": job_registry,
    }

    def __init__(self) -> None:
        super().__init__()

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        # Override of an abstract method for the class of checks to do with
        # a specific resource type (in this case 'jobs')
        # This is specific to how the IaC is broken into checkable subcomponents
        return self.block_type_registries["jobs"]

    @staticmethod
    def _parse_file(
        f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        # EDIT" add conditional here to ensure this file is something we should parse.
        # Below is this example for github actions
        # as the file is always located in a predictable path
        # There should always be a conditional otherwise you'll parse ALL files.
        if ".github/workflows/" in os.path.abspath(f):
            return YamlRunner._parse_file(f)

        return None


#   An abstract function placeholder to determine the start and end lines.
#   If the default doesn't work you'll need to add your own version here
#    def get_start_end_lines(self, end, result_config, start):
