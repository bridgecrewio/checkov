from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class CloudwatchLogGroupEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure CloudWatch logs are encrypted at rest using KMS CMKs"
        id = "CKV_AWS_97"
        supported_resources = ['aws_cloudwatch_log_group']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        """
            Looks for encryption configuration at cloudtrail:
            https://www.terraform.io/docs/providers/aws/r/cloudtrail.html
        :param conf: cloudtrail configuration
        :return: <CheckResult>
        """
        return 'kms_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = CloudwatchLogGroupEncryption()
