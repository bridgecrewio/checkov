from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck as BaseCheck


class TestSQLServerAdminLoginPasswordNotHardCoded(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that 'Administrator Login Password' is not hard-coded for SQL servers"
        id = "CKV_AZURE_160"
        supported_resources = ['azurerm_sql_server', 
                               'azurerm_postgresql_server', 
                               'azurerm_postgresql_flexible_server']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Argument for Administrator password is subtlely different for 'azurerm_postgresql_flexible_server'
        if 'administrator_login_password' in conf.keys():
            self.evaluated_keys = ['administrator_login_password']
            password = conf.get("administrator_login_password")[0]
        elif 'administrator_password' in conf.keys():
            self.evaluated_keys = ['administrator_password']
            password = conf.get("administrator_password")[0]
        else:
            return CheckResult.FAILED

        if BaseCheck._is_variable_dependant(password):
            return CheckResult.PASSED
        return CheckResult.FAILED

check = TestSQLServerAdminLoginPasswordNotHardCoded()
