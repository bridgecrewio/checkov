from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class EMRPubliclyAccessible(BaseResourceCheck):

    def __init__(self):
        name = "Ensure AWS EMR block public access setting is enabled"
        id = "CKV_AWS_390"
        supported_resources = ['aws_emr_block_public_access_configuration']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'block_public_security_group_rules' in conf:
            if str(conf['block_public_security_group_rules'][0]).lower() == "false":
                return CheckResult.FAILED
        return CheckResult.PASSED


check = EMRPubliclyAccessible()
