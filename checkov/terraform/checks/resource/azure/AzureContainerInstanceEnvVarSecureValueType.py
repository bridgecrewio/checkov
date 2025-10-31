from __future__ import annotations
from typing import Any, List
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

import itertools


class AzureContainerInstanceEnvVarSecureValueType(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure container environment variables are configured with secure values only"
        id = "CKV_AZURE_235"
        supported_resources = ("azurerm_container_group",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:

        for container in itertools.chain(conf.get('container', {}), conf.get('init_container', {})):
            if "environment_variables" in container:
                return CheckResult.FAILED
            return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['container', 'init_container']


check = AzureContainerInstanceEnvVarSecureValueType()
