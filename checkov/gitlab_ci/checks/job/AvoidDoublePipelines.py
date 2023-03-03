from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.gitlab_ci.checks.base_gitlab_ci_check import BaseGitlabCICheck
from checkov.yaml_doc.enums import BlockType

PIPELINE_SOURCES = ('$CI_PIPELINE_SOURCE == "merge_request_event"', '$CI_PIPELINE_SOURCE == "push"')


class AvoidDoublePipelines(BaseGitlabCICheck):
    def __init__(self) -> None:
        name = "Avoid creating rules that generate double pipelines"
        id = "CKV_GITLABCI_2"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=('*.rules',)
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        c = 0

        for rule in conf:
            if isinstance(rule, dict) and "if" in rule:
                value = rule['if']
                if value.startswith(PIPELINE_SOURCES):
                    c += 1
                    if c > 1:
                        return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf


check = AvoidDoublePipelines()
