from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class S3AccessPointPubliclyAccessible(BaseResourceCheck):

    def __init__(self):
        name = "Ensure AWS S3 access point block public access setting is enabled"
        id = "CKV_AWS_392"
        supported_resources = ['aws_s3_access_point']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'public_access_block_configuration' in conf:
            block_config_list = conf['public_access_block_configuration']
            if isinstance(block_config_list, list):
                block_config = block_config_list[0]
                if ('ignore_public_acls' in block_config and block_config['block_public_acls'] == [False] and
                        'block_public_policy' in block_config and block_config['block_public_policy'] == [False] and
                        'restrict_public_buckets' in block_config and
                        block_config['restrict_public_buckets'] == [False]):
                    self.evaluated_keys = ['public_access_block_configuration.block_public_acls',
                                           'public_access_block_configuration.restrict_public_buckets']
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = S3AccessPointPubliclyAccessible()
