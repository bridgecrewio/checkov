from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ACRAnonymousPullDisabled(BaseResourceCheck):
    ANONYMOUS_PULL_SKUS = {"Standard", "Premium"}  # noqa: CCE003  # a static attribute

    def __init__(self):
        name = "Ensures that ACR disables anonymous pulling of images"
        id = "CKV_AZURE_138"
        supported_resources = ("azurerm_container_registry",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # anonymous_pull_enabled only applies to Standard and Premium skus, by default is set to false
        if (
            "sku" in conf.keys()
            and isinstance(conf["sku"][0], str)
            and conf["sku"][0] in ACRAnonymousPullDisabled.ANONYMOUS_PULL_SKUS
            and "anonymous_pull_enabled" in conf.keys()
            and conf["anonymous_pull_enabled"][0]
        ):
            return CheckResult.FAILED

        return CheckResult.PASSED


check = ACRAnonymousPullDisabled()
