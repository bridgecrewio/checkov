from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DefaultServiceAccountBinding(BaseResourceCheck):
    def __init__(self):
        # CIS-1.5 5.1.5
        name = "Ensure that default service accounts are not actively used"
        # Check no role/clusterrole is bound to a default service account (to ensure not actively used)
        id = "CKV_K8S_42"
        supported_resources = ["kubernetes_role_binding", "kubernetes_role_binding_v1",
                               "kubernetes_cluster_role_binding", "kubernetes_cluster_role_binding_v1"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if "subject" in conf:
            for idx, subject in enumerate(conf["subject"]):
                if subject["kind"] == ["ServiceAccount"]:
                    if subject["name"] == ["default"]:
                        self.evaluated_keys = [f"subject/[{idx}]/name"]
                        return CheckResult.FAILED
        return CheckResult.PASSED


check = DefaultServiceAccountBinding()
