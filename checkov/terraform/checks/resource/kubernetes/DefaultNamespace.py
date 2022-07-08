from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DefaultNamespace(BaseResourceCheck):
    def __init__(self):
        # CIS-1.5 5.7.4
        name = "The default namespace should not be used"
        id = "CKV_K8S_21"
        supported_resources = ["kubernetes_pod", "kubernetes_deployment", "kubernetes_daemonset",
                               "kubernetes_stateful_set", "kubernetes_replication_controller", "kubernetes_job",
                               "kubernetes_cron_job", "kubernetes_service", "kubernetes_secret",
                               "kubernetes_service_account", "kubernetes_role_binding", "kubernetes_config_map",
                               "kubernetes_ingress"]

        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if "metadata" not in conf:
            self.evaluated_keys = [""]
            return CheckResult.FAILED
        metadata = conf.get('metadata')[0]
        if metadata.get('namespace'):
            if metadata.get('namespace') == ["default"]:
                self.evaluated_keys = ['metadata/[0]/namespace']
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.FAILED


check = DefaultNamespace()
