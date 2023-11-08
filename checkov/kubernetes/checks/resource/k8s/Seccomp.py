from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check
from checkov.common.util.type_forcers import force_list


class Seccomp(BaseK8Check):

    def __init__(self) -> None:
        # CIS-1.5 5.7.2
        name = "Ensure that the seccomp profile is set to docker/default or runtime/default"
        id = "CKV_K8S_31"
        # Location: Pod.metadata.annotations.seccomp.security.alpha.kubernetes.io/pod
        # Location: CronJob.spec.jobTemplate.spec.template.metadata.annotations.seccomp.security.alpha.kubernetes.io/pod
        # Location: *.spec.template.metadata.annotations.seccomp.security.alpha.kubernetes.io/pod
        # Location: *.spec.securityContext.seccompProfile.type
        supported_kind = ('Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet', 'ReplicationController', 'Job', 'CronJob')
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf: dict[str, Any]) -> CheckResult:
        metadata = {}

        if conf['kind'] == 'Pod':
            security_profile = find_in_dict(conf, 'spec/securityContext/seccompProfile/type')
            if security_profile:
                return CheckResult.PASSED if security_profile == 'RuntimeDefault' else CheckResult.FAILED
            if "metadata" in conf:
                metadata = conf["metadata"]
            if "spec" in conf and isinstance(conf["spec"], dict):
                containers = conf["spec"].get("containers")
                if containers:
                    containers = force_list(containers)
                    num_containers = len(containers)
                    passed_containers = 0
                    for container in containers:
                        security_profile = find_in_dict(container, "securityContext/seccompProfile/type")
                        if security_profile:
                            if security_profile == "RuntimeDefault":
                                passed_containers += 1
                            else:
                                return CheckResult.FAILED
                    if passed_containers == num_containers:
                        return CheckResult.PASSED

        if conf['kind'] in ['Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'ReplicaSet']:
            security_profile = find_in_dict(conf, 'spec/template/spec/securityContext/seccompProfile/type')
            if security_profile:
                return CheckResult.PASSED if security_profile == 'RuntimeDefault' else CheckResult.FAILED

            metadata = find_in_dict(input_dict=conf, key_path="spec/template/metadata")
            if not metadata and "metadata" in conf:
                metadata = conf["metadata"]
        elif conf['kind'] == 'CronJob':
            inner_template = find_in_dict(input_dict=conf, key_path="spec/jobTemplate/spec/template")
            if inner_template and isinstance(inner_template, dict):
                if "metadata" in inner_template:
                    metadata = inner_template["metadata"]
                elif "spec" in inner_template:
                    inner_spec = inner_template["spec"]
                    if "metadata" in inner_spec:
                        metadata = inner_spec["metadata"]
                    elif "securityContext" in inner_spec:
                        security_profile = inner_spec["securityContext"].get("seccompProfile", {}).get("type")
                        return CheckResult.PASSED if security_profile == 'RuntimeDefault' else CheckResult.FAILED
        else:
            inner_metadata = find_in_dict(input_dict=conf, key_path="spec/template/metadata")
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
