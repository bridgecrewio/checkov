from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RedShiftSSL(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Redshift uses SSL"
        id = "CKV_AWS_105"
        supported_resources = ['aws_redshift_parameter_group']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        if 'parameter' in conf:
            for elem in conf["parameter"]:
                if isinstance(elem, dict) and elem["name"][0] == "require_ssl" and elem["value"] == [True]:
                    self.evaluated_keys = [f'parameter/[{conf["parameter"].index(elem)}]/name', f'parameter/[{conf["parameter"].index(elem)}]/value']
                    return CheckResult.PASSED

            #no matching params
            return CheckResult.FAILED

        else:
          # no params at all
          return CheckResult.FAILED


check = RedShiftSSL()
