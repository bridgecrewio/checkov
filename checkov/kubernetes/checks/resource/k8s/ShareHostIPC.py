from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class ShareHostIPC(BaseK8Check):
    def __init__(self) -> None:
        # CIS-1.3 1.7.3
        # CIS-1.5 5.2.3
        name = "Containers should not share the host IPC namespace"
        id = "CKV_K8S_18"
        # Location: Pod.spec.hostIPC
        # Location: CronJob.spec.jobTemplate.spec.template.spec.hostIPC
        # Location: *..spec.template.spec.hostIPC
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
            spec = conf.get("spec")
            if spec:
                job_template = spec.get("jobTemplate")
                if job_template:
                    job_template_spec = job_template.get("spec")
                    if job_template_spec:
                        template = job_template_spec.get("template")
                        if template:
                            if "spec" in template:
                                spec = template["spec"]
        else:
            inner_spec = self.get_inner_entry(conf, "spec")
            spec = inner_spec if inner_spec else spec
        if spec:
            if "hostIPC" in spec:
                if spec["hostIPC"]:
                    return CheckResult.FAILED
                else:
                    return CheckResult.PASSED
            return CheckResult.PASSED
        return CheckResult.FAILED


check = ShareHostIPC()
