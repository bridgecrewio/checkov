from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories, CheckResult


class LambdaDLQConfigured(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that AWS Lambda function is configured for a Dead Letter Queue(DLQ)"
        id = "CKV_AWS_116"
        supported_resources = ["AWS::Lambda::Function", "AWS::Serverless::Function"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        properties = conf.get("Properties")
        if properties:
            self.evaluated_keys = ["Properties/DeadLetterConfig/TargetArn"]
            dlc = properties.get("DeadLetterConfig")
            if dlc and dlc.get("TargetArn"):
                return CheckResult.PASSED

            self.evaluated_keys.append("Properties/DeadLetterQueue/TargetArn")
            dlq = properties.get("DeadLetterQueue")
            if dlq and dlq.get("TargetArn"):
                return CheckResult.PASSED

        return CheckResult.FAILED


check = LambdaDLQConfigured()
