from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.resource_scanner import ResourceScanner


class S3PublicACLScanner(ResourceScanner):
    def __init__(self):
        name = "S3 Bucket has an ACL defined which allows public access."
        scan_id = "BC_AWS_S3_1"
        supported_resources = ['aws_s3_bucket']
        categories = [ScanCategories.GENERAL_SECURITY]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for ACL configuration at aws_s3_bucket:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <ScanResult>
        """
        if 'acl' in conf.keys():
            acl_block = conf['acl']
            if acl_block in [["public-read"],["public-read-write"],["website"]]:
                return ScanResult.FAILURE
        return ScanResult.SUCCESS


scanner = S3PublicACLScanner()
