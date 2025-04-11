from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SecretsManagerSecretEncrypted(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Secrets Manager secret is encrypted using KMS CMK"
        id = "CKV_AWS_149"
        supported_resources = ("awscc_secretsmanager_secret",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "kms_key_id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = SecretsManagerSecretEncrypted()
