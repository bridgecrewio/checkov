from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class DefaultNamespace(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.7.4
        name = "The default namespace should not be used"
        id = "CKV_K8S_21"
        supported_kind = ['Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet', 'ReplicationController', 'Job', 'CronJob', 'Service', 'Secret', 'ServiceAccount', 'Role', 'RoleBinding', 'ConfigMap', 'Ingress']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        if "namespace" in conf["metadata"]:
            return "{}.{}.{}".format(conf["kind"], conf["metadata"]["name"], conf["metadata"]["namespace"])
        else:
            return "{}.{}.default".format(conf["kind"], conf["metadata"]["name"])

    def scan_spec_conf(self, conf):
        if "metadata" in conf:
            if "namespace" in conf["metadata"]:
                if conf["metadata"]["namespace"] != "default":
                    return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.FAILED

check = DefaultNamespace()