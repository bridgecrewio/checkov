from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.resource_scanner import ResourceScanner


class PasswordPolicyReuse(ResourceScanner):
    def __init__(self):
        name = "Ensure IAM password policy prevents password reuse"
        scan_id = "AWS_CIS_1_10"
        supported_resource = 'aws_iam_account_password_policy'
        categories = [ScanCategories.IAM]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resource=supported_resource)

    def scan_resource_conf(self, conf):
        """
            validates iam password policy
            https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy.html
        :param conf: aws_iam_account_password_policy configuration
        :return: <ScanResult>
        """
        key = 'password_reuse_prevention'
        if key in conf.keys():
            if conf[key] >= 24:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = PasswordPolicyReuse()
