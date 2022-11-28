from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class RedshiftServerlessNamespaceKMSKey(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Redshift Serverless namespace is encrypted by KMS using a customer managed key (CMK)"
        id = "CKV_AWS_282"
        supported_resources = ('aws_redshiftserverless_namespace',)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "kms_key_id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = RedshiftServerlessNamespaceKMSKey()
