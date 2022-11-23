from __future__ import annotations

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ACRGeoreplicated(BaseResourceCheck):

    def __init__(self):

        # Check to see the sku is set to premium with any replication block set

        name = "Ensure geo-replicated container registries to match multi-region container deployments."
        id = "CKV_AZURE_165"
        supported_resources = ("azurerm_container_registry",)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        sku = conf.get('sku')
        if sku:
            if sku[0] == "Premium":
                replication = conf.get('georeplications')
                if replication:
                    return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.FAILED


check = ACRGeoreplicated()
