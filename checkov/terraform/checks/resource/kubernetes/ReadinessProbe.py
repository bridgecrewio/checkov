from typing import Any
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ReadinessProbe(BaseResourceValueCheck):

    def __init__(self):
        name = "Readiness Probe Should be Configured"
        id = "CKV_K8S_9"
        supported_resources = ["kubernetes_pod", "kubernetes_pod_v1",
                               "kubernetes_deployment", "kubernetes_deployment_v1"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        if "kubernetes_deployment" == self.entity_type or "kubernetes_deployment_v1" == self.entity_type:
            return "spec/[0]/template/[0]/spec/[0]/container/[0]/readiness_probe/[0]"
        return "spec/[0]/container/[0]/readiness_probe/[0]"

    def scan_resource_conf(self, conf) -> CheckResult:
        spec = conf.get('spec', [None])[0]
        if not spec:
            return CheckResult.UNKNOWN

        evaluated_keys_path = "spec"

        template = spec.get("template")
        if template and isinstance(template, list):
            template = template[0]
            template_spec = template.get("spec")
            if template_spec and isinstance(template_spec, list):
                spec = template_spec[0]
                evaluated_keys_path = f'{evaluated_keys_path}/[0]/template/[0]/spec'

        if isinstance(spec, dict) and spec:
            containers = spec.get("container")
            if containers is None:
                return CheckResult.UNKNOWN
            for idx, container in enumerate(containers):
                if not isinstance(container, dict):
                    return CheckResult.UNKNOWN
                if container.get("readiness_probe"):
                    return CheckResult.PASSED
                self.evaluated_keys = [f'{evaluated_keys_path}/[0]/container/[{idx}]']
                return CheckResult.FAILED

        return CheckResult.FAILED

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = ReadinessProbe()
