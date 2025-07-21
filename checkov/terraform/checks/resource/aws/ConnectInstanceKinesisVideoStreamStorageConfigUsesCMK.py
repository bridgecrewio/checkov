from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class ConnectInstanceKinesisVideoStreamStorageConfigUsesCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Connect Instance Kinesis Video Stream Storage Config uses CMK"
        id = "CKV_AWS_269"
        supported_resources = ['aws_connect_instance_storage_config']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'storage_config/[0]/kinesis_video_stream_config/[0]/encryption_config/[0]/key_id'

    def get_expected_value(self):
        return ANY_VALUE

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
        Looks for encryption key_id in kinesis_video_stream_config
        """
        storage_config = conf.get("storage_config")
        if storage_config and isinstance(storage_config, list):
            if "kinesis_video_stream_config" in storage_config[0]:
                return super().scan_resource_conf(conf)
        return CheckResult.UNKNOWN


check = ConnectInstanceKinesisVideoStreamStorageConfigUsesCMK()
