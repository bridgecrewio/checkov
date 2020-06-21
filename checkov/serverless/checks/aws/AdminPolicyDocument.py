from checkov.serverless.checks.base_function_check import BaseFunctionCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.serverless.parsers.parser import

class AdminPolicyDocument(BaseFunctionCheck):
    def __init__(self):
        name = "Ensure IAM policies that allow full \"*-*\" administrative privileges are not created"
        id = "CKV_AWS_1"
        supported_entities = ['aws']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def scan_function_conf(self, conf):
        """
            validates iam policy document
            https://learn.hashicorp.com/terraform/aws/iam-policy
        :param conf: aws_kms_key configuration
        :return: <CheckResult>
        """
        key = 'statement'
        if key in conf.keys():
            for statement in conf[key]:
                if 'actions' in statement and statement.get('effect', ['Allow'])[0] == 'Allow' and '*' in statement['actions'][0] \
                        and '*' in statement['resources'][0]:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = AdminPolicyDocument()
