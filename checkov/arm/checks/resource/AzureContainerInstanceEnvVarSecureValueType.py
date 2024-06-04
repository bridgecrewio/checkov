from __future__ import annotations
from typing import Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck

import itertools


class AzureContainerInstanceEnvVarSecureValueType(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure container environment variables are configured with secure values only"
        id = "CKV_AZURE_235"
        supported_resources = ("Microsoft.ContainerInstance/containerGroups",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        containers = itertools.chain(
            conf.get('properties', {}).get('containers', []),
            conf.get('properties', {}).get('initContainers', [])
        )
       for container in containers:
            env_vars = container.get('properties', {}).get('environmentVariables', [])
            if env_vars is not None and any('value' in env_var for env_var in env_vars):
                return CheckResult.FAILED
        return CheckResult.PASSED


check = AzureContainerInstanceEnvVarSecureValueType()
