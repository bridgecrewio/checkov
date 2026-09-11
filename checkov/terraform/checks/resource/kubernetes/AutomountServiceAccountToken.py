from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AutomountServiceAccountToken(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure pods are not automatically mounting service account tokens"
        id = "CKV_K8S_50"
        supported_resources = ['kubernetes_pod', 'kubernetes_pod_v1',
                               'kubernetes_deployment', 'kubernetes_deployment_v1']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "spec" not in conf:
            return CheckResult.FAILED
        spec = conf['spec'][0]
        if not spec:
            return CheckResult.UNKNOWN

        # Handle deployment templates
        template = spec.get("template")
        if template and isinstance(template, list):
            template = template[0]
            template_spec = template.get("spec")
            if template_spec and isinstance(template_spec, list):
                spec = template_spec[0]

        # Check if automount_service_account_token is explicitly set to False
        automount = spec.get("automount_service_account_token")
        if automount is not None:
            if isinstance(automount, list):
                automount = automount[0]
            if automount is False:
                return CheckResult.PASSED

        return CheckResult.FAILED


check = AutomountServiceAccountToken()
