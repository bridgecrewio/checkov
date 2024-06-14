from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceCheck


class CDBInternetService(BaseResourceCheck):
    def __init__(self):
        name = "Ensure CDB not enable internet service"
        id = "CKV_TC_9"
        supported_resources = ['tencentcloud_mysql_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("internet_service") and conf["internet_service"][0] == 1:
                  return CheckResult.FAILED
                
        return CheckResult.PASSED

check = CDBInternetService()
