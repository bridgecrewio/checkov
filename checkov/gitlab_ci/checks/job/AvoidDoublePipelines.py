from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.gitlab_ci.checks.base_gitlab_ci_check import BaseGitlabCICheck
from checkov.yaml_doc.enums import BlockType


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
        pipeline_sources = ('$CI_PIPELINE_SOURCE == "merge_request_event"', '$CI_PIPELINE_SOURCE == "push"')
        for x in conf:
            if "if" in x:
                value = x['if']
                if value.startswith(pipeline_sources):
                    c += 1
                if c > 1:
                    return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf
        

check = AvoidDoublePipelines()
