
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class DefaultServiceAccountBinding(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.1.5
        name = "Ensure that default service accounts are not actively used"
        # Check no role/clusterrole is bound to a default service account (to ensure not actively used)
        id = "CKV_K8S_42"
        supported_kind = ['RoleBinding', 'ClusterRoleBinding']
        # Location: .subjects[]
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf):
        if "subjects" in conf:
            for subject in conf["subjects"]:
                if subject["kind"] == "ServiceAccount":
                    if subject["name"] == "default":
                        return CheckResult.FAILED
        return CheckResult.PASSED

check = DefaultServiceAccountBinding()



