from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AzureContainerInstanceEnvVarSecureValueType(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure container environment variables are configured with secure values only"
        id = "CKV_AZURE_234"
        supported_resources = ("azurerm_container_group",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:

        if any(container.get('secure_environment_variables') for container in
               conf.get('container') or conf.get('init_container')):
            ContainerBlocksWithSecureValue = [container for container in
                                              conf.get('container') or conf.get('init_container') if
                                              container.get('secure_environment_variables')]
            for ContSecValues in ContainerBlocksWithSecureValue:
                ExplodedContainerSecureValues = ContSecValues['secure_environment_variables'][0]
                if len(ExplodedContainerSecureValues) > 0:
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED

        else:
            return CheckResult.FAILED


check = AzureContainerInstanceEnvVarSecureValueType()
