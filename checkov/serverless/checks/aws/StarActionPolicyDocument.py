from checkov.serverless.checks.base_function_check import BaseFunctionCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.serverless.parsers.parser import IAM_ROLE_STATEMENTS_TOKEN


class StarActionPolicyDocument(BaseFunctionCheck):
    def __init__(self):
        name = "Ensure no IAM policies documents allow \"*\" as a statement's actions"
        id = "CKV_AWS_49"
        supported_entities = ['serverless_aws']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def scan_function_conf(self, conf):
        """
        validates iam policy document
         https://learn.hashicorp.com/terraform/aws/iam-policy
        :param conf: aws_kms_key configuration
        :return: <CheckResult>
        """
        key = IAM_ROLE_STATEMENTS_TOKEN
        if key in conf.keys():
            for statement in conf[key]:
                if 'Action' in statement and '*' in statement['Action'] and statement.get('Effect') == 'Allow':
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = StarActionPolicyDocument()
