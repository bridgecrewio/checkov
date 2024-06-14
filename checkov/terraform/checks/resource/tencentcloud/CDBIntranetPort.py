from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceCheck


class CDBIntranetPort(BaseResourceCheck):
    def __init__(self):
        name = "Ensure CDB intranet port not equal 3306"
        id = "CKV_TC_10"
        supported_resources = ['tencentcloud_mysql_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("intranet_port") and conf["intranet_port"][0] == 3306:
                  return CheckResult.FAILED
                
        return CheckResult.PASSED

check = CDBIntranetPort()
