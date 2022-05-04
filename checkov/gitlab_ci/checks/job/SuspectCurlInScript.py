from checkov.common.models.enums import CheckResult

from checkov.gitlab_ci.checks.base_gitlab_ci_check import BaseGitlabCICheck
from checkov.yaml_doc.enums import BlockType


class SuspectCurlInScript(BaseGitlabCICheck):
    def __init__(self):
        name = "Suspicious use of curl with CI environment variables in script"
        id = "CKV_GITLABCI_1"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=['*.script[]']
        )

    def scan_entity_conf(self, conf):
        if "curl" in conf:
            badstuff = ['curl','$CI_']
            lines = conf.split("\n")
            for line in lines:
                if all(x in line for x in badstuff):
                    return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf

check = SuspectCurlInScript()
