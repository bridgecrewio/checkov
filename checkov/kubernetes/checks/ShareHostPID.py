from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class ShareHostPID(BaseK8Check):

    def __init__(self):
        # CIS-1.3 1.7.2
        # CIS-1.5 5.2.2
        name = "Containers should not share the host process ID namespace"
        id = "CKV_K8S_17"
        # Location: Pod.spec.hostPID
        # Location: CronJob.spec.jobTemplate.spec.template.spec.hostPID
        # Location: *.spec.template.spec.hostPID
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
            inner_spec = self.get_inner_entry(conf, "spec")
            spec = inner_spec if inner_spec else spec
        if spec:
            if "hostPID" in spec:
                if spec["hostPID"]:
                    return CheckResult.FAILED
                else:
                    return CheckResult.PASSED
            return CheckResult.PASSED
        return CheckResult.FAILED

check = ShareHostPID()