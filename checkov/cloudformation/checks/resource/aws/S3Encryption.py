from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class S3Encryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure the S3 bucket has server-side-encryption enabled"
        id = "CKV_AWS_19"
        supported_resources = ['AWS::S3::Bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('Properties'):
            if conf['Properties'].get('ServerSideEncryptionRule') or \
                (conf['Properties'].get('BucketEncryption') and
                 len(conf['Properties']['BucketEncryption'].get('ServerSideEncryptionConfiguration', [])) > 0):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = S3Encryption()
