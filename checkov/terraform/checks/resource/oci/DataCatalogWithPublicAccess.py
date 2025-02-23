# DataCatalogWithPublicAccess
from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DataCatalogWithPublicAccess(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure OCI Data Catalog is configured without overly permissive network access"
        id = "CKV_OCI_23"
        supported_resources = ['oci_datacatalog_catalog']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        if "attached_catalog_private_endpoints" in conf:
            if len(conf["attached_catalog_private_endpoints"][0]) > 0:
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['attached_catalog_private_endpoints']


check = DataCatalogWithPublicAccess()
