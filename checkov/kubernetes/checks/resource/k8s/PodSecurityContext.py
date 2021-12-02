
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class PodSecurityContext(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.7.3
        name = "Apply security context to your pods and containers"
        # Security context can be set at pod or container level.
        id = "CKV_K8S_29"
        # Location: Pod.spec.securityContext
        # Location: CronJob.spec.jobTemplate.spec.template.spec.securityContext
        # Location: *.spec.template.spec.securityContext
        supported_kind = ['Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet', 'ReplicationController', 'Job', 'CronJob']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

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
            if spec.get("securityContext"):
                if spec["securityContext"]:
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = PodSecurityContext()
