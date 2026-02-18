from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class LambdaDLQConfigured(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that AWS Lambda function is configured with a Dead Letter Queue"
        id = "CKV_AWS_117"
        supported_resources = ['awscc_lambda_function']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('dead_letter_config'):
            if isinstance(conf['dead_letter_config'], list) and len(conf['dead_letter_config']) > 0:
                if conf['dead_letter_config'][0].get('target_arn'):
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self):
        return ['dead_letter_config/target_arn']


check = LambdaDLQConfigured()
