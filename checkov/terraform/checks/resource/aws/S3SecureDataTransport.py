from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class S3SecureDataTransport(BaseResourceCheck):
    def __init__(self):
        name = "Ensure AWS S3 bucket is configured with secure data transport policy"
        id = "CKV_AWS_799" # UPDATE
        supported_resources = ('aws_s3_bucket_acl',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        acl = conf.get('acl')
        if acl and acl[0] in ('public-read', 'public-read-write'):
            # Search for a connected aws_s3_bucket then a connected aws_s3_bucket_public_access_block then check if restrict_public_buckets is true and pass or else fail
            # if connected to aws_s3_bucket_website_configuration then pass
            # Ensures the aws:SecureTransport condition does not exist in any policy statement.
            return CheckResult.FAILED

        access_control_policy = conf.get('access_control_policy')
        if access_control_policy:
            grants = access_control_policy[0].get('grant', [])
            for grant in grants:
                grantee = grant.get('grantee', [])
                if grantee and grantee[0].get('uri', [None])[0] == 'http://acs.amazonaws.com/groups/global/AllUsers':
                    # Search for a connected aws_s3_bucket then a connected aws_s3_bucket_public_access_block then check if block_public_acls is true and pass or else fail
                    # if connected to aws_s3_bucket_website_configuration then pass
                    # Ensures the aws:SecureTransport condition does not exist in any policy statement.
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = S3SecureDataTransport()
