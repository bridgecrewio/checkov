from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check
from checkov.common.util.type_forcers import force_list


class Seccomp(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.7.2
        name = "Ensure that the seccomp profile is set to docker/default or runtime/default"
        id = "CKV_K8S_31"
        # Location: Pod.metadata.annotations.seccomp.security.alpha.kubernetes.io/pod
        # Location: CronJob.spec.jobTemplate.spec.template.metadata.annotations.seccomp.security.alpha.kubernetes.io/pod
        # Location: *.spec.template.metadata.annotations.seccomp.security.alpha.kubernetes.io/pod
        # Location: *.spec.securityContext.seccompProfile.type
        supported_kind = ['Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet', 'ReplicationController', 'Job', 'CronJob']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf):
        metadata = {}

        if conf['kind'] == 'Pod':
            security_profile = find_in_dict(conf, 'spec/securityContext/seccompProfile/type')
            if security_profile:
                return CheckResult.PASSED if security_profile == 'RuntimeDefault' else CheckResult.FAILED
            if "metadata" in conf:
                metadata = conf["metadata"]
        if conf['kind'] in ['Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'ReplicaSet']:
            security_profile = find_in_dict(conf, 'spec/template/spec/securityContext/seccompProfile/type')
            if security_profile:
                return CheckResult.PASSED if security_profile == 'RuntimeDefault' else CheckResult.FAILED

            metadata = self.get_inner_entry(conf, "metadata")
            if not metadata and "metadata" in conf:
                metadata = conf["metadata"]
        elif conf['kind'] == 'CronJob':
            if "spec" in conf:
                if "jobTemplate" in conf["spec"]:
                    if "spec" in conf["spec"]["jobTemplate"]:
                        if "template" in conf["spec"]["jobTemplate"]["spec"]:
                            if "metadata" in conf["spec"]["jobTemplate"]["spec"]["template"]:
                                metadata = conf["spec"]["jobTemplate"]["spec"]["template"]["metadata"]
        else:
            inner_metadata = self.get_inner_entry(conf, "metadata")
            metadata = inner_metadata if inner_metadata else metadata

        if metadata:
            if metadata.get('annotations'):
                for annotation in force_list(metadata["annotations"]):
                    for key in annotation:
                        if "seccomp.security.alpha.kubernetes.io/pod" in key:
                            if "docker/default" in annotation[key] or "runtime/default" in annotation[key]:
                                return CheckResult.PASSED
        return CheckResult.FAILED


check = Seccomp()
