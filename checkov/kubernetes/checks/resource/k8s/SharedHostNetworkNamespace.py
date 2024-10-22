from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class SharedHostNetworkNamespace(BaseK8Check):
    def __init__(self) -> None:
        # CIS-1.3 1.7.4
        # CIS-1.5 5.2.4
        name = "Containers should not share the host network namespace"
        id = "CKV_K8S_19"
        # Location: Pod.spec.hostNetwork
        # Location: CronJob.spec.jobTemplate.spec.template.spec.hostNetwork
        # Location: *.spec.template.spec.hostNetwork
        supported_kind = (
            "Pod",
            "Deployment",
            "DaemonSet",
            "StatefulSet",
            "ReplicaSet",
            "ReplicationController",
            "Job",
            "CronJob",
        )
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf: dict[str, Any]) -> CheckResult:
        spec = {}

        if conf["kind"] == "Pod":
            if "spec" in conf:
                spec = conf["spec"]
        elif conf["kind"] == "CronJob":
            inner_spec = find_in_dict(input_dict=conf, key_path="spec/jobTemplate/spec/template/spec")
            spec = inner_spec if inner_spec else spec
        else:
            inner_spec = find_in_dict(input_dict=conf, key_path="spec/template/spec")
            spec = inner_spec if inner_spec else spec
        if spec:
            if "hostNetwork" in spec:
                if spec["hostNetwork"]:
                    return CheckResult.FAILED

        # This value is by default set to false
        return CheckResult.PASSED


check = SharedHostNetworkNamespace()
