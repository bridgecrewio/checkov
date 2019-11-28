from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.scanner import Scanner


class PasswordPolicyLength(Scanner):
    def __init__(self):
        name = "Ensure IAM password policy requires minimum length of 14 or greater"
        scan_id = "BC_AWS_IAM_9"
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
        key = 'minimum_password_length'
        if key in conf.keys():
            if conf[key] >= 14:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = PasswordPolicyLength()
