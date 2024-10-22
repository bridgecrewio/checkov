from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class EMRClusterConfEncryptsInTransit(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure EMR Cluster security configuration encrypts InTransit"
        id = "CKV_AWS_351"
        supported_resources = ("aws_emr_security_configuration",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        security_conf = conf.get("configuration")
        if security_conf and isinstance(security_conf, list) and isinstance(security_conf[0], dict):
            transit_encrypt = find_in_dict(
                input_dict=security_conf[0],
                key_path="EncryptionConfiguration/EnableInTransitEncryption",
            )
            if transit_encrypt:
                return CheckResult.PASSED

            return CheckResult.FAILED

        return CheckResult.UNKNOWN


check = EMRClusterConfEncryptsInTransit()
