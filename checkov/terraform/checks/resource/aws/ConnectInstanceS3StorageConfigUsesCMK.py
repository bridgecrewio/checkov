from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class ConnectInstanceS3StorageConfigUsesCMK(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Connect Instance S3 Storage Config uses CMK"
        id = "CKV_AWS_270"
        supported_resources = ("aws_connect_instance_storage_config",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if conf.get("resource_type") and conf.get("resource_type")[0] in (
            "CHAT_TRANSCRIPTS",
            "CALL_RECORDINGS",
            "SCHEDULED_REPORTS",
            "MEDIA_STREAMS",
            "CONTACT_TRACE_RECORDS",
            "AGENT_EVENTS",
        ):
            return super().scan_resource_conf(conf)
        return CheckResult.UNKNOWN

    def get_inspected_key(self) -> str:
        return "storage_config/[0]/s3_config/[0]/encryption_config/[0]/key_id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = ConnectInstanceS3StorageConfigUsesCMK()
