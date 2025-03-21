from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class S3AccessPointPubliclyAccessible(BaseResourceCheck):

    def __init__(self):
        name = "AWS S3 access point Block public access setting disabled"
        id = "CKV_AWS_392"
        supported_resources = ['aws_s3_access_point']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'public_access_block_configuration' in conf:
            for arg in list(conf['public_access_block_configuration'][0].keys()):
                if arg == 'restrict_public_buckets':
                    if str(conf['public_access_block_configuration'][0][arg][0]).lower() == 'false':
                        return CheckResult.FAILED
                    else:
                        return CheckResult.PASSED
        return CheckResult.PASSED


check = S3AccessPointPubliclyAccessible()
