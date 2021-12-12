from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class DefaultNamespace(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.7.4
        name = "The default namespace should not be used"
        # default Service Account and Service/kubernetes are ignored
        id = "CKV_K8S_21"
        supported_kind = ['Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet', 'ReplicationController', 'Job', 'CronJob', 'Service', 'Secret', 'ServiceAccount', 'Role', 'RoleBinding', 'ConfigMap', 'Ingress']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf):
        if "metadata" in conf:
            if "namespace" in conf["metadata"]:
                if conf["metadata"]["namespace"] != "default":
                    return CheckResult.PASSED
                else:
                    if conf["kind"] == "ServiceAccount" and conf["metadata"]["name"] == "default":
                        return CheckResult.PASSED
                    if conf["kind"] == "Service" and conf["metadata"]["name"] == "kubernetes":
                        return CheckResult.PASSED
            # If namespace not defined it is default -> Ignore default Service account and kubernetes service
            if conf["kind"] == "ServiceAccount" and conf["metadata"]["name"] == "default":
                return CheckResult.PASSED
            if conf["kind"] == "Service" and conf["metadata"]["name"] == "kubernetes":
                return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.FAILED

check = DefaultNamespace()