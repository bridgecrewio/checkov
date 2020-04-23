from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class LivenessProbe(BaseK8Check):

    def __init__(self):
        name = "Liveness Probe Should be Configured"
        id = "CKV_K8S_8"
        supported_kind = ['Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        if conf['kind'] == 'Pod':
            return 'Pod.spec.containers[]'
        else:
            return conf['kind'] + '.spec.template.spec.containers[]'

    def scan_spec_conf(self, conf):
        if conf['kind'] == 'Pod':
            if "spec" in conf:
                if "containers" in conf["spec"]:
                    for container in conf["spec"]["containers"]:
                        if "livenessProbe" not in container:
                            return CheckResult.FAILED
                    return CheckResult.PASSED
        else:
            if "spec" in conf:
                if "template" in conf["spec"]:
                    if "spec" in conf["spec"]["template"]:
                        if "containers" in conf["spec"]["template"]["spec"]:
                            for container in conf["spec"]["template"]["spec"]["containers"]:
                                if "livenessProbe" not in container:
                                    return CheckResult.FAILED
                            return CheckResult.PASSED
        return CheckResult.FAILED

check = LivenessProbe()