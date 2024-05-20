from __future__ import annotations
from typing import Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class CosmosDBLocalAuthDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        # This is the full description of your check
        description = "Ensure that Local Authentication is disabled on CosmosDB"

        # This is the Unique ID for your check
        id = "CKV_AZURE_140"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ('Microsoft.DocumentDB/databaseAccounts',)

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = (CheckCategories.IAM,)
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "kind" in conf:
            if conf["kind"] == "GlobalDocumentDB":
                return super().scan_resource_conf(conf)
            return CheckResult.UNKNOWN

    def get_inspected_key(self) -> str:
        return "properties/disableLocalAuth"

    def get_expected_value(self) -> Any:
        return True


check = CosmosDBLocalAuthDisabled()
