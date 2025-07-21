from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class ConnectInstanceKinesisVideoStreamStorageConfigUsesCMK(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Connect Instance Kinesis Video Stream Storage Config uses CMK"
        id = "CKV_AWS_269"
        supported_resources = ("aws_connect_instance_storage_config",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if conf.get("resource_type") == ["VIDEO_STREAMS"]:
            return super().scan_resource_conf(conf)
        return CheckResult.UNKNOWN

    def get_inspected_key(self) -> str:
        return "storage_config/[0]/kinesis_video_stream_config/[0]/encryption_config/[0]/key_id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = ConnectInstanceKinesisVideoStreamStorageConfigUsesCMK()
