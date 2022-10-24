from typing import List

from checkov.common.parsers.node import DictNode
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class SecretManagerSecretEncrypted(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Secrets Manager secret is encrypted using KMS CMK"
        id = "CKV_AWS_149"
        supported_resources = ["AWS::SecretsManager::Secret"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: DictNode) -> CheckResult:
        aws_kms_alias = "aws/"
        properties = conf.get("Properties")
        if properties:
            kms_key_id = properties.get("KmsKeyId")
            if kms_key_id and aws_kms_alias not in kms_key_id:
                return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['Properties/KmsKeyId']


check = SecretManagerSecretEncrypted()
