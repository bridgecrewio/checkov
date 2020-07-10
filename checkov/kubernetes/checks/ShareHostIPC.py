from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class ShareHostIPC(BaseK8Check):

    def __init__(self):
        # CIS-1.3 1.7.3
        # CIS-1.5 5.2.3
        name = "Containers should not share the host IPC namespace"
        id = "CKV_K8S_18"
        # Location: Pod.spec.hostIPC
        # Location: CronJob.spec.jobTemplate.spec.template.spec.hostIPC
        # Location: *..spec.template.spec.hostIPC
        supported_kind = ['Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet', 'ReplicationController', 'Job', 'CronJob']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        if "namespace" in conf["metadata"]:
            return "{}.{}.{}".format(conf["kind"], conf["metadata"]["name"], conf["metadata"]["namespace"])
        else:
            return "{}.{}.default".format(conf["kind"], conf["metadata"]["name"])

    def scan_spec_conf(self, conf):
        spec = {}

        if conf['kind'] == 'Pod':
            if "spec" in conf:
                spec = conf["spec"]
        elif conf['kind'] == 'CronJob':
            if "spec" in conf:
                if "jobTemplate" in conf["spec"]:
                    if "spec" in conf["spec"]["jobTemplate"]:
                        if "template" in conf["spec"]["jobTemplate"]["spec"]:
                            if "spec" in conf["spec"]["jobTemplate"]["spec"]["template"]:
                                spec = conf["spec"]["jobTemplate"]["spec"]["template"]["spec"]
        else:
            if "spec" in conf:
                if "template" in conf["spec"]:
                    if "spec" in conf["spec"]["template"]:
                        spec = conf["spec"]["template"]["spec"]
        if spec:
            if "hostIPC" in spec:
                if spec["hostIPC"]:
                    return CheckResult.FAILED
                else:
                    return CheckResult.PASSED
            return CheckResult.PASSED
        return CheckResult.FAILED

check = ShareHostIPC()