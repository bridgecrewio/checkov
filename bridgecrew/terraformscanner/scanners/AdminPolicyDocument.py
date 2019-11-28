from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.scanner import Scanner


class AdminPolicyDocument(Scanner):
    def __init__(self):
        name = "Ensure IAM policies that allow full \"*-*\" administrative privileges are not created"
        scan_id = "BC_AWS_IAM_23"
        supported_resource = 'aws_iam_policy_document'
        categories = [ScanCategories.GENERAL_SECURITY]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resource=supported_resource)

    def scan_resource_conf(self, conf):
        """
            validates iam policy document
            https://learn.hashicorp.com/terraform/aws/iam-policy
        :param conf: aws_kms_key configuration
        :return: <ScanResult>
        """
        key = 'statement'
        if key in conf.keys():
            if conf[key]['actions'] == ["*"] and conf[key]['resources'] == ["*"]:
                return ScanResult.FAILURE
        return ScanResult.SUCCESS


scanner = AdminPolicyDocument()
