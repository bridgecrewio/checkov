from __future__ import annotations

from typing import List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class TransferServerAllowsOnlySecureProtocols(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Transfer Server allows only secure protocols"
        id = "CKV_AWS_357"
        supported_resources = ("aws_transfer_server",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        protocols = conf.get("protocols")
        if protocols and isinstance(protocols, list):
            if "FTP" in protocols[0]:
                return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["protocols"]


check = TransferServerAllowsOnlySecureProtocols()
