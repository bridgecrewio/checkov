from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ECSTaskDefinitionEFSVolumeEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Encryption in transit is enabled for EFS volumes in ECS Task definitions"
        id = "CKV_AWS_97"
        supported_resources = ("AWS::ECS::TaskDefinition",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("Properties")
        if properties and isinstance(properties, dict):
            volumes = properties.get("Volumes")
            if volumes and isinstance(volumes, list):
                for volume in volumes:
                    efs_config = volume.get("EFSVolumeConfiguration")
                    if efs_config and isinstance(efs_config, dict):
                        if efs_config.get("TransitEncryption") == "ENABLED":
                            return CheckResult.PASSED
                        else:
                            return CheckResult.FAILED

        return CheckResult.PASSED


check = ECSTaskDefinitionEFSVolumeEncryption()
