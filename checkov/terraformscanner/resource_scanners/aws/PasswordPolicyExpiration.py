from checkov.terraformscanner.models.enums import ScanResult, ScanCategories
from checkov.terraformscanner.resource_scanner import ResourceScanner

class PasswordPolicyExpiration(ResourceScanner):
    def __init__(self):
        name = "Ensure IAM password policy expires passwords within 90 days or less"
        scan_id = "BC_AWS_IAM_11"
        supported_resources = ['aws_iam_account_password_policy']
        categories = [ScanCategories.IAM]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            validates iam password policy
            https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy.html
        :param conf: aws_iam_account_password_policy configuration
        :return: <ScanResult>
        """
        key = 'max_password_age'
        if key in conf.keys():
            if conf[key] >= 90:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE
scanner = PasswordPolicyExpiration()