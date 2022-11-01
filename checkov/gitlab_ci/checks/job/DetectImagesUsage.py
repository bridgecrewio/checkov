from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.gitlab_ci.checks.base_gitlab_ci_check import BaseGitlabCICheck
from checkov.yaml_doc.enums import BlockType


class DetectImageUsage(BaseGitlabCICheck):
    def __init__(self) -> None:
        name = "Detecting image usages in gitlab workflows"
        id = "CKV_GITLABCI_3"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=('*.image[]', '*.services[]')
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        return CheckResult.PASSED, conf


check = DetectImageUsage()
