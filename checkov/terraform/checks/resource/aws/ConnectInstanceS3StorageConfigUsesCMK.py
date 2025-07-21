from typing import Any, Dict, List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class ConnectInstanceS3StorageConfigUsesCMK(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Connect Instance S3 Storage Config uses CMK"
        id = "CKV_AWS_270"
        supported_resources = ("aws_connect_instance_storage_config",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "storage_config/[0]/s3_config/[0]/encryption_config/[0]/key_id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
        Looks for encryption key_id in s3_config
        """
        storage_config = conf.get("storage_config")
        if storage_config and isinstance(storage_config, list):
            if "s3_config" in storage_config[0]:
                return super().scan_resource_conf(conf)
        return CheckResult.UNKNOWN


check = ConnectInstanceS3StorageConfigUsesCMK()
