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
        if 'parameter' not in conf:
            return CheckResult.FAILED
        self.evaluated_keys = ['parameter']
        for idx, elem in enumerate(conf["parameter"]):
            if isinstance(elem, dict) and elem["name"][0] == "require_ssl" and elem["value"] == [True]:
                self.evaluated_keys = [f'parameter/[{idx}]/name', f'parameter/[{idx}]/value']
                return CheckResult.PASSED

        #no matching params
        return CheckResult.FAILED


check = RedShiftSSL()
