from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class MSSQLServerMinTLSVersion(BaseResourceCheck):
    def __init__(self):
        name = "Ensure MSSQL is using the latest version of TLS encryption"
        id = "CKV_AZURE_52"
        supported_resources = ['azurerm_mssql_server']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'minimum_tls_version' in conf:
            if conf['minimum_tls_version'][0] != '1.2':
                return CheckResult.FAILED
            else:
                return CheckResult.PASSED
        else:
            return CheckResult.FAILED    
        

check = MSSQLServerMinTLSVersion()
