from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class K8SEtcdKMSEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure etcd database is encrypted with KMS key."
        id = "CKV_YC_10"
        supported_resources = ("yandex_kubernetes_cluster",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "kms_provider/[0]/key_id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = K8SEtcdKMSEncryption()
