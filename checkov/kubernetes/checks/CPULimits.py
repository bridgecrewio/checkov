from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class CPULimits(BaseK8Check):

    def __init__(self):
        name = "CPU limits should be set"
        id = "CKV_K8S_11"
        supported_kind = ['Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        if conf['kind'] == 'Pod':
            return 'Pod.spec.containers[].resources.limits.cpu'
        else:
            return conf['kind'] + '.spec.template.spec.containers[].resources.limits.cpu'

    def scan_spec_conf(self, conf):
        if conf['kind'] == 'Pod':
            if "spec" in conf:
                if "containers" in conf["spec"]:
                    for container in conf["spec"]["containers"]:
                        if "resources" in container:
                            if "limits" in container["resources"]:
                                if "cpu" not in container["resources"]["limits"]:
                                    return CheckResult.FAILED
                            else:
                                return CheckResult.FAILED
                        else:
                            return CheckResult.FAILED
                    return CheckResult.PASSED
        else:
            if "spec" in conf:
                if "template" in conf["spec"]:
                    if "spec" in conf["spec"]["template"]:
                        if "containers" in conf["spec"]["template"]["spec"]:
                            for container in conf["spec"]["template"]["spec"]["containers"]:
                                if "resources" in container:
                                    if "limits" in container["resources"]:
                                        if "cpu" not in container["resources"]["limits"]:
                                            return CheckResult.FAILED
                                    else:
                                        return CheckResult.FAILED
                                else:
                                    return CheckResult.FAILED
                            return CheckResult.PASSED
        return CheckResult.FAILED

check = CPULimits()