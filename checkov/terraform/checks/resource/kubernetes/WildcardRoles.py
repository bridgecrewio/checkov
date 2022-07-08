
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class WildcardRoles(BaseResourceCheck):

    def __init__(self):
        name = "Minimize wildcard use in Roles and ClusterRoles"
        id = "CKV_K8S_49"
        supported_resources = ["kubernetes_role", "kubernetes_cluster_role"]

        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        rules = conf.get("rule")
        if isinstance(rules, list) and rules:
            for rule in rules:
                if "api_groups" in rule:
                    if "*" in rule["api_groups"][0]:
                        return CheckResult.FAILED
                if "resources" in rule:
                    if "*" in rule["resources"][0]:
                        return CheckResult.FAILED
                if "verbs" in rule:
                    if "*" in rule["verbs"][0]:
                        return CheckResult.FAILED

        return CheckResult.PASSED


check = WildcardRoles()
