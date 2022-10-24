from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DefaultServiceAccount(BaseResourceCheck):
    def __init__(self) -> None:
        # CIS-1.5 5.1.5
        name = "Ensure that default service accounts are not actively used"
        # Check automountServiceAccountToken in default service account in runtime
        id = "CKV_K8S_41"
        supported_resources = ["kubernetes_service_account", "kubernetes_service_account_v1"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "metadata" in conf:
            if "name" in conf["metadata"][0]:
                metadata = conf["metadata"][0]
                if metadata["name"] == ["default"]:
                    if "automount_service_account_token" in conf:
                        if conf["automount_service_account_token"] == [False]:
                            return CheckResult.PASSED
                    self.evaluated_keys = ["metadata/[0]/name"]
                    return CheckResult.FAILED
                else:
                    return CheckResult.PASSED
        return CheckResult.PASSED


check = DefaultServiceAccount()
