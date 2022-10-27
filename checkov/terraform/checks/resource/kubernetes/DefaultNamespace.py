from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DefaultNamespace(BaseResourceCheck):
    def __init__(self):
        # CIS-1.5 5.7.4
        name = "The default namespace should not be used"
        id = "CKV_K8S_21"
        supported_resources = ["kubernetes_pod", "kubernetes_pod_v1",
                               "kubernetes_deployment", "kubernetes_deployment_v1",
                               "kubernetes_daemonset", "kubernetes_daemon_set_v1",
                               "kubernetes_stateful_set", "kubernetes_stateful_set_v1",
                               "kubernetes_replication_controller", "kubernetes_replication_controller_v1",
                               "kubernetes_job", "kubernetes_job_v1",
                               "kubernetes_cron_job", "kubernetes_cron_job_v1",
                               "kubernetes_service", "kubernetes_service_v1",
                               "kubernetes_secret", "kubernetes_secret_v1",
                               "kubernetes_service_account", "kubernetes_service_account_v1",
                               "kubernetes_role_binding", "kubernetes_role_binding_v1",
                               "kubernetes_config_map", "kubernetes_config_map_v1",
                               "kubernetes_ingress", "kubernetes_ingress_v1"]

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
