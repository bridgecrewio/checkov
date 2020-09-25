from checkov.serverless.checks.function.base_function_check import BaseFunctionCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.serverless.parsers.parser import IAM_ROLE_STATEMENTS_TOKEN


class S3ListWildcard(BaseFunctionCheck):
    def __init__(self):
        name = "Ensure no Bucket policies allow 's3:List*' action"
        id = "CKV_AWS_88"
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
                if 'Action' in statement and 's3:List*' in statement['Action'] and statement.get('Effect') == 'Allow':
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = S3ListWildcard()
