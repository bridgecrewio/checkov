from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check

class WildcardRoles(BaseK8Check):
    # CIS-1.6 5.1.3
    def __init__(self):
        name = "Minimize wildcard use in Roles and ClusterRoles"
        id = "CKV_K8S_49"
        categories = [CheckCategories.KUBERNETES]
        supported_kind = ['Role', 'ClusterRole']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf):
        if isinstance(conf.get("rules"), list) and len(conf.get("rules")) > 0:
            if "apiGroups" in conf["rules"][0]:
                if any("*" in s for s in conf["rules"][0]["apiGroups"]):
                    return CheckResult.FAILED
            if "resources" in conf["rules"][0]:
                if any("*" in s for s in conf["rules"][0]["resources"]):
                    return CheckResult.FAILED
            if "verbs" in conf["rules"][0]:
                if any("*" in s for s in conf["rules"][0]["verbs"]):
                    return CheckResult.FAILED

        return CheckResult.PASSED

check = WildcardRoles()
