from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class S3IgnorePublicACLs(BaseResourceCheck):
    def __init__(self):
        name = "Ensure S3 bucket has ignore public ACLs enabled"
        id = "CKV_AWS_55"
        supported_resources = ['AWS::S3::Bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('Properties') and conf['Properties'].get('PublicAccessBlockConfiguration'):
            public_access_block_conf = conf['Properties']['PublicAccessBlockConfiguration']
            if public_access_block_conf['IgnorePublicAcls']:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = S3IgnorePublicACLs()
