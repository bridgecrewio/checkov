from checkov.common.models.enums import CheckResult

from checkov.gitlab_ci.checks.base_gitlab_ci_check import BaseGitlabCICheck
from checkov.yaml_doc.enums import BlockType


class AvoidDoublePipelines(BaseGitlabCICheck):
    def __init__(self):
        name = "Avoid creating rules that generate double pipelines"
        id = "CKV_GITLABCI_2"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=['*.rules']
        )

    def scan_entity_conf(self, conf):
        c = 0
        for x in conf:
            if "if" in x:
                value = x['if']
                if value.startswith('$CI_PIPELINE_SOURCE'):
                    c += 1
                if c > 1:
                    return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf
        

check = AvoidDoublePipelines()
