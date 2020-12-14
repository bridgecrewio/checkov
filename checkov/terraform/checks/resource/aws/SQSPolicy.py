import json

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SQSPolicy(BaseResourceCheck):
    def __init__(self):
        name = "Ensure SQS policy does not allow ALL (*) actions."
        id = "CKV_AWS_72"
        supported_resources = ['aws_sqs_queue_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for public * policy for SQS repository:
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue_policy
        :param conf: aws_sqs_queue_policy configuration
        :return: <CheckResult>
        """
        if "policy" in conf.keys():
            if is_json(conf["policy"][0]):
                if json.loads(conf["policy"][0])['Statement'][0]['Action'] == '*':
                    return CheckResult.FAILED
        return CheckResult.PASSED


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


check = SQSPolicy()
