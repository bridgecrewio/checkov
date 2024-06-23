from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.util.data_structures_utils import find_in_dict


class DatabricksWorkspaceDBFSRootEncryptedWithCustomerManagedKey(BaseResourceCheck):
    def __init__(self) -> None:
        # https://learn.microsoft.com/en-us/azure/templates/microsoft.databricks/workspaces?pivots=deployment-language-arm-template#workspaceencryptionparameter-1
        name = "Ensure that Databricks Workspaces enables customer-managed key for root DBFS encryption"
        id = "CKV2_AZURE_48"
        supported_resources = ("Microsoft.Databricks/workspaces",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        parameters = conf.get("properties", {}).get("parameters")
        prepare_encryption = find_in_dict(input_dict=parameters, key_path="prepareEncryption/value")
        if not prepare_encryption or str(prepare_encryption).lower() != "true":
            return CheckResult.FAILED

        encryption_settings = find_in_dict(input_dict=parameters, key_path="encryption/value")
        if not encryption_settings:
            return CheckResult.FAILED

        return CheckResult.PASSED


check = DatabricksWorkspaceDBFSRootEncryptedWithCustomerManagedKey()
