from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class S3MFADelete(BaseResourceCheck):


    def __init__(self):
        name = "Ensure S3 bucket has MFA delete enabled"
        id = "CKV_AWS_52"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):

        if 'versioning' in conf.keys():
            versioning_block = conf['versioning']
            for block in versioning_block:
                if 'mfa_delete' in block.keys():
                    if block['mfa_delete']:

                        return CheckResult.PASSED
        return CheckResult.FAILED

scanner = S3MFADelete()
