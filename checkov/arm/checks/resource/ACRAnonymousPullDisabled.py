from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class ACRAnonymousPullDisabled(BaseResourceCheck):
    ANONYMOUS_PULL_SKUS = {"Standard", "Premium"}  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        name = "Ensures that ACR disables anonymous pulling of images"
        id = "CKV_AZURE_138"
        supported_resources = ("Microsoft.ContainerRegistry/registries",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("properties", {})

        anonymousPullEnabled = properties.get("anonymousPullEnabled")

        sku = conf.get("sku")

        if (
                sku is not None
                and isinstance(sku.get("name"), str)
                and sku.get("name") in ACRAnonymousPullDisabled.ANONYMOUS_PULL_SKUS
                and properties
                and anonymousPullEnabled
        ):
            return CheckResult.FAILED

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['properties', 'properties/anonymousPullEnabled', 'sku']


check = ACRAnonymousPullDisabled()
