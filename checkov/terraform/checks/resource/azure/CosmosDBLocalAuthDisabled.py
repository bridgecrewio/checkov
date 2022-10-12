from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class CosmosDBLocalAuthDisabled(BaseResourceCheck):
    def __init__(self) -> None:
        # This is the full description of your check
        description = "Ensure that Local Authentication is disabled on CosmosDB"

        # This is the Unique ID for your check
        id = "CKV_AZURE_140"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ('azurerm_cosmosdb_account',)

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = (CheckCategories.IAM,)
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if isinstance(conf['kind'], list) and conf['kind'] == ["GlobalDocumentDB"]:
            if 'local_authentication_disabled' in conf:
                if isinstance(conf['local_authentication_disabled'], list) and conf['local_authentication_disabled'] == [True]:
                    return CheckResult.PASSED
            self.evaluated_keys = ['local_authentication_disabled']
            return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = CosmosDBLocalAuthDisabled()
