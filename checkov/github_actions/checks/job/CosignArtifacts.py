from checkov.common.models.enums import CheckResult
from checkov.common.util.consts import START_LINE
from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.yaml_doc.enums import BlockType


class CosignSignPresent(BaseGithubActionsCheck):
    def __init__(self):
        name = "Find evidence of cosign sign execution in pipeline"
        id = "CKV_GHA_5"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.OBJECT,
            supported_entities=['jobs']
        )

    def scan_entity_conf(self, conf):
        for jobname, jobdetail in conf.items():
            if jobname == START_LINE:
                return CheckResult.FAILED, conf
            steps = jobdetail.get("steps")
            if steps:
                for step in steps:
                    run = step.get("run","none")
                    if "cosign sign" in run:
                        return CheckResult.PASSED, step
        return CheckResult.FAILED, conf


check = CosignSignPresent()
