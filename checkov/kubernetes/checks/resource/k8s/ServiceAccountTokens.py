from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class ServiceAccountTokens(BaseK8Check):
    def __init__(self) -> None:
        # CIS-1.5 5.1.6
        name = "Ensure that Service Account Tokens are only mounted where necessary"
        # Check automountServiceAccountToken in Pod spec and/or containers
        # Location: Pod.spec.automountServiceAccountToken
        # Location: CronJob.spec.jobTemplate.spec.template.spec.automountServiceAccountToken
        # Location: *.spec.template.spec.automountServiceAccountToken
        id = "CKV_K8S_38"
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

        # Collect results
        if spec:
            if not isinstance(spec, dict):
                return CheckResult.UNKNOWN
            if spec.get("automountServiceAccountToken") is False:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = ServiceAccountTokens()
