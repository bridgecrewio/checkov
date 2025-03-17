from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class S3BucketPubliclyReadableViaACL(BaseResourceCheck):

    def __init__(self):
        name = "AWS S3 buckets are accessible to public via ACL"
        id = "CKV_AWS_393"
        supported_resources = ['aws_s3_bucket_acl']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'acl' in conf:
            if conf['acl'][0] == 'public-read':
                return CheckResult.FAILED
        return CheckResult.PASSED


check = S3BucketPubliclyReadableViaACL()
