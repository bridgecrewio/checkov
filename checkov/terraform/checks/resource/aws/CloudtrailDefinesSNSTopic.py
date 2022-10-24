from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class CloudtrailDefinesSNSTopic(BaseResourceValueCheck):
    def __init__(self):
        """
        If you CloudTrail trails are not referenced to an SNS topic,
        you can't get notifications each time Amazon CloudTrail
        publishes any new log files, and you lose the ability to take realtime actions.

        AWS: "An active account can generate a large number of notifications. If you subscribe with email or SMS,
        you can receive a large volume of messages.
        We recommend that you subscribe using Amazon Simple Queue Service (Amazon SQS), which lets you
        handle notifications programmatically.
        """
        name = "Ensure CloudTrail defines an SNS Topic"
        id = "CKV_AWS_252"
        supported_resources = ['aws_cloudtrail']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        """
            Looks for SNS topic at cloudtrail:
            https://www.terraform.io/docs/providers/aws/r/cloudtrail.html
        :param conf: cloudtrail configuration
        :return: <CheckResult>
        """
        return 'sns_topic_name'

    def get_expected_value(self):
        return ANY_VALUE


check = CloudtrailDefinesSNSTopic()
