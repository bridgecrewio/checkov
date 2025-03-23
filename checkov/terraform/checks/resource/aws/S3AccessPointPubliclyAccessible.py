from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class S3AccessPointPubliclyAccessible(BaseResourceCheck):

    def __init__(self):
        name = "Ensure AWS S3 access point block public access setting is enabled"
        id = "CKV_AWS_392"
        supported_resources = ['aws_s3_account_public_access_block']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'restrict_public_buckets' in conf:
            x = str(conf['restrict_public_buckets'][0]).lower()
            if str(conf['restrict_public_buckets'][0]).lower() == 'false':
                return CheckResult.FAILED
        return CheckResult.PASSED


check = S3AccessPointPubliclyAccessible()
