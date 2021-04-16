from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_parameter_check import BaseParameterCheck

class SecureStringParameterNoHardcodedValue(BaseParameterCheck):
    def __init__(self):
        # apiVersion 2017-08-03 and 2018-03-31 = Fail - No authorized IP range available
        # apiVersion 2019-02-01, 2019-04-01, 2019-06-01 - Preview
        # apiversion 2019-08-01 and greater are fully supported
        name = "SecureString parameters should not have hardcoded default values"
        id = "CKV_AZURE_987"
        supported_resources = ['secureString']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('defaultValue'):
            return CheckResult.FAILED
        else:
            return CheckResult.PASSED


check = SecureStringParameterNoHardcodedValue()
