from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class EMRClusterConfEncryptsLocalDisk(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure EMR Cluster security configuration encrypts local disks"
        id = "CKV_AWS_349"
        supported_resources = ("aws_emr_security_configuration",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        security_conf = conf.get("configuration")
        if security_conf and isinstance(security_conf, list) and isinstance(security_conf[0], dict):
            encrypt_conf = security_conf[0].get("EncryptionConfiguration")
            if encrypt_conf and isinstance(encrypt_conf, dict) and encrypt_conf.get("EnableAtRestEncryption") is True:
                local_encrypt = find_in_dict(
                    input_dict=encrypt_conf,
                    key_path="AtRestEncryptionConfiguration/LocalDiskEncryptionConfiguration",
                )
                if local_encrypt:
                    return CheckResult.PASSED

            return CheckResult.FAILED

        return CheckResult.UNKNOWN


check = EMRClusterConfEncryptsLocalDisk()
