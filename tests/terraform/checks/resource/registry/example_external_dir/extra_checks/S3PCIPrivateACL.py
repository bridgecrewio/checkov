from lark import Token

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class S3PCIPrivateACL(BaseResourceCheck):
    def __init__(self):
        name = "Ensure PCI Scope buckets has private ACL (enable public ACL for non-pci buckets)"
        id = "CKV_AWS_999"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for ACL configuration at aws_s3_bucket and Tag values:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <CheckResult>
        """
        if 'tags' in conf.keys():
            environment_tag = Token("IDENTIFIER", "Scope")
            if environment_tag in conf['tags'][0].keys():
                if conf['tags'][0][environment_tag] == "PCI":
                    if 'acl' in conf.keys():
                        acl_block = conf['acl']
                        if acl_block in [["public-read"], ["public-read-write"], ["website"]]:
                            return CheckResult.FAILED
        return CheckResult.PASSED


scanner = S3PCIPrivateACL()
