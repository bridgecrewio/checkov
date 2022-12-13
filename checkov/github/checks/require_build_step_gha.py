from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.github.base_github_gha_check import BaseGHACheck



class GithubWorkflowsRequireBuildStep(BaseGHACheck):
    def __init__(self) -> None:
        name = "Ensure all build steps are defined as code"
        id = "CKV_GITHUB_30"
        super().__init__(id=id, name=name)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult | None:  # type:ignore[override]
        ckv_metadata, conf = self.resolve_ckv_metadata_conf(conf=conf)
        if 'workflow' in ckv_metadata.get('file_name', ''):
            if self.is_gha_enabled(ckv_metadata=ckv_metadata):
                for workflow in conf['workflows']:
                    workflow_name = workflow.get('name', '')
                    if self.is_build_workflow(workflow_name=workflow_name) or \
                            self.workflow_contain_build(workflow_content=workflow['parsed_content']):
                        return CheckResult.PASSED
                # didn't find any build job
                return CheckResult.FAILED
            return None


check = GithubWorkflowsRequireBuildStep()
