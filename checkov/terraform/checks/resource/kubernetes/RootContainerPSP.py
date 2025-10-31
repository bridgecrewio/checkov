from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RootContainersPSP(BaseResourceCheck):

    def __init__(self):
        # CIS-1.3 1.7.6
        # CIS-1.5 5.2.6
        name = "Do not admit root containers"
        id = "CKV_K8S_6"
        supported_resources = ['kubernetes_pod_security_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        # required param
        if "spec" in conf:
            self.evaluated_keys = ["spec"]
            # required param
            if "run_as_user" in conf["spec"][0]:
                self.evaluated_keys = ["spec/[0]/run_as_user"]
                runas = conf["spec"][0]["run_as_user"][0]
                if runas["rule"]:
                    self.evaluated_keys = ["spec/[0]/run_as_user/[0]/rule"]
                    inspected_value = runas["rule"][0]
                    if inspected_value == "MustRunAsNonRoot":
                        return CheckResult.PASSED
                    elif inspected_value == "MustRunAs":
                        if runas["range"]:
                            for item in runas["range"]:
                                if item["min"][0] == 0:
                                    return CheckResult.FAILED
                            return CheckResult.PASSED
        return CheckResult.FAILED


check = RootContainersPSP()
