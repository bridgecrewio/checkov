from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ECSClusterLoggingEncryptedWithCMK(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure ECS Cluster logging is enabled and client to container communication uses CMK"
        id = "CKV_AWS_224"
        supported_resources = ("aws_ecs_cluster",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        configuration = conf.get("configuration")
        if configuration and isinstance(configuration, list) and isinstance(configuration[0], dict):
            execute_command = configuration[0].get("execute_command_configuration")
            if execute_command and isinstance(execute_command, list):
                execute_command = execute_command[0]
                if isinstance(execute_command, dict) and not execute_command.get("logging") == ["NONE"]:
                    if execute_command.get("kms_key_id"):
                        log_conf = execute_command.get("log_configuration")
                        if log_conf and isinstance(log_conf, list):
                            log_conf = log_conf[0]
                            if isinstance(log_conf, dict) and (
                                log_conf.get("cloud_watch_encryption_enabled") == [True]
                                or log_conf.get("s3_bucket_encryption_enabled") == [True]
                            ):
                                return CheckResult.PASSED

                    return CheckResult.FAILED

        return CheckResult.UNKNOWN


check = ECSClusterLoggingEncryptedWithCMK()
