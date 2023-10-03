from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CPULimits(BaseResourceCheck):
    def __init__(self) -> None:
        name = "CPU Limits should be set"
        id = "CKV_K8S_11"
        supported_resources = ['kubernetes_pod', 'kubernetes_pod_v1',
                               'kubernetes_deployment', 'kubernetes_deployment_v1']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "spec" not in conf:
            self.evaluated_keys = [""]
            return CheckResult.FAILED
        spec = conf['spec'][0]
        evaluated_keys_path = "spec"
        if not spec:
            return CheckResult.UNKNOWN

        template = spec.get("template")
        if template and isinstance(template, list):
            template = template[0]
            template_spec = template.get("spec")
            if template_spec and isinstance(template_spec, list):
                spec = template_spec[0]
                evaluated_keys_path = f'{evaluated_keys_path}/[0]/template/[0]/spec'

        containers = spec.get("container")
        if not containers:
            return CheckResult.UNKNOWN
        for idx, container in enumerate(containers):
            if not isinstance(container, dict):
                return CheckResult.UNKNOWN
            if container.get("resources"):
                resources = container.get("resources")[0]
                if resources.get('limits'):
                    limits = resources.get('limits')[0]
                    if isinstance(limits, dict) and limits.get('cpu'):
                        return CheckResult.PASSED
                    self.evaluated_keys = [f'{evaluated_keys_path}/[0]/container/[{idx}]/resources/[0]/limits']
                    return CheckResult.FAILED
                self.evaluated_keys = [f'{evaluated_keys_path}/[0]/container/[{idx}]/resources']
                return CheckResult.FAILED
            self.evaluated_keys = [f'{evaluated_keys_path}/[0]/container/[{idx}]']
            return CheckResult.FAILED
        return CheckResult.PASSED


check = CPULimits()
