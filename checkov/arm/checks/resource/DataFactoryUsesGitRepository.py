from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class DataFactoryUsesGitRepository(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Data Factory uses Git repository for source control"
        id = "CKV_AZURE_103"
        supported_resources = ["Microsoft.DataFactory/factories"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if conf.get("properties") and isinstance(conf.get("properties"), dict):
            properties = conf.get("properties")
            if properties.get("repoConfiguration") and not isinstance(properties.get("repoConfiguration"), str):
                repo = properties.get("repoConfiguration")
                if repo.get("type") is not None:
                    return CheckResult.PASSED
            if properties.get("repoConfiguration") is None or properties.get("repoConfiguration") == "":
                return CheckResult.FAILED
            return CheckResult.UNKNOWN
        self.evaluated_keys = ['properties']
        return CheckResult.FAILED


check = DataFactoryUsesGitRepository()
