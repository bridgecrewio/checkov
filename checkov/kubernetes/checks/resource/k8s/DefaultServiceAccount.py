
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class DefaultServiceAccount(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.1.5
        name = "Ensure that default service accounts are not actively used"
        # Check automountServiceAccountToken in default service account in runtime
        id = "CKV_K8S_41"
        supported_kind = ['ServiceAccount']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf):
        if "metadata" in conf:
            if "name" in conf["metadata"]:
                if conf["metadata"]["name"] == "default":
                    if "automountServiceAccountToken" in conf:
                        if conf["automountServiceAccountToken"] is False:
                            return CheckResult.PASSED
                    return CheckResult.FAILED
                else:
                    return CheckResult.PASSED
        return CheckResult.PASSED

check = DefaultServiceAccount()



