import re

from checkov.common.models.enums import CheckResult
from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.yaml_doc.enums import BlockType


class CosignSignSBOM(BaseGithubActionsCheck):
    def __init__(self):
        name = "Find evidence of cosign sbom attestation in pipeline"
        id = "CKV_GHA_6"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.OBJECT,
            supported_entities=['jobs']
        )

    def scan_entity_conf(self, conf):
        jobs = conf.items()
        for jobname,jobdetail in jobs:
            if jobname == '__startline__':
                return CheckResult.FAILED, conf
            steps = jobdetail.get("steps")
            if steps is not None:
                for step in steps:
                    run = step.get("run","none")
                    if re.search('(?=.*cosign)(?=.*sbom)', run):
                        return CheckResult.PASSED, step
        return CheckResult.FAILED, conf


check = CosignSignSBOM()
