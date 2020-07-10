
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class Seccomp(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.7.2
        name = "Ensure that the seccomp profile is set to docker/default or runtime/default"
        id = "CKV_K8S_31"
        # Location: Pod.metadata.annotations.seccomp.security.alpha.kubernetes.io/pod
        # Location: CronJob.spec.jobTemplate.spec.template.metadata.annotations.seccomp.security.alpha.kubernetes.io/pod
        # Location: *.spec.template.metadata.annotations.seccomp.security.alpha.kubernetes.io/pod
        supported_kind = ['Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet', 'ReplicationController', 'Job', 'CronJob']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        if "namespace" in conf["metadata"]:
            return "{}.{}.{}".format(conf["kind"], conf["metadata"]["name"], conf["metadata"]["namespace"])
        else:
            return "{}.{}.default".format(conf["kind"], conf["metadata"]["name"])

    def scan_spec_conf(self, conf):
        metadata = {}

        if conf['kind'] == 'Pod':
            if "metadata" in conf:
                metadata = conf["metadata"]
        elif conf['kind'] == 'CronJob':
            if "spec" in conf:
                if "jobTemplate" in conf["spec"]:
                    if "spec" in conf["spec"]["jobTemplate"]:
                        if "template" in conf["spec"]["jobTemplate"]["spec"]:
                            if "metadata" in conf["spec"]["jobTemplate"]["spec"]["template"]:
                                metadata = conf["spec"]["jobTemplate"]["spec"]["template"]["metadata"]
        else:
            if "spec" in conf:
                if "template" in conf["spec"]:
                    if "metadata" in conf["spec"]["template"]:
                        metadata = conf["spec"]["template"]["metadata"]

        if metadata:
            if "annotations" in metadata and isinstance(metadata['annotations'], dict):
                if "seccomp.security.alpha.kubernetes.io/pod" in metadata["annotations"]:
                    if ("docker/default" in metadata["annotations"]["seccomp.security.alpha.kubernetes.io/pod"] or
                    "runtime/default" in metadata["annotations"]["seccomp.security.alpha.kubernetes.io/pod"]):
                        return CheckResult.PASSED
        return CheckResult.FAILED

check = Seccomp()
