from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DataFactoryUsesGitRepository(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Data Factory uses Git repository for source control"
        id = "CKV_AZURE_103"
        supported_resources = ["azurerm_data_factory"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        github = conf.get("github_configuration", [{}])[0]
        if isinstance(github, dict) and github.get("repository_name"):
            self.evaluated_keys = ['github_configuration/[0]/repository_name']
            return CheckResult.PASSED
        vsts = conf.get("vsts_configuration", [{}])[0]
        if isinstance(vsts, dict) and vsts.get("repository_name"):
            self.evaluated_keys = ['vsts_configuration/[0]/repository_name']
            return CheckResult.PASSED
        self.evaluated_keys = ['github_configuration', 'vsts_configuration']
        return CheckResult.FAILED


check = DataFactoryUsesGitRepository()
