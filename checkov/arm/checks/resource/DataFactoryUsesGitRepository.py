from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class DataFactoryUsesGitRepository(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Data Factory uses Git repository for source control"
        id = "CKV_AZURE_103"
        supported_resources = ("Microsoft.DataFactory/factories",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("properties")
        if properties and isinstance(properties, dict):
            self.evaluated_keys = ["properties/repoConfiguration/type"]
            repo = properties.get("repoConfiguration")
            if not repo:
                return CheckResult.FAILED
            if repo and isinstance(repo, dict) and repo.get("type") is not None:
                return CheckResult.PASSED
            return CheckResult.UNKNOWN
        return CheckResult.FAILED


check = DataFactoryUsesGitRepository()
