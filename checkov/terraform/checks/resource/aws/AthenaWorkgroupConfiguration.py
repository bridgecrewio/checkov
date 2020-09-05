from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AthenaWorkgroupConfiguration(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Athena Workgroup should enforce configuration to prevent client disabling encryption"
        id = "CKV_AWS_82"
        supported_resources = ['aws_athena_workgroup']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'configuration' in conf.keys():
            if 'enforce_workgroup_configuration' in conf['configuration'][0]:
                if conf['configuration'][0]['enforce_workgroup_configuration'] is True:
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = AthenaWorkgroupConfiguration()
