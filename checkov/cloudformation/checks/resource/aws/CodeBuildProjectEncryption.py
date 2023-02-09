from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class CodeBuildProjectEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that CodeBuild Project encryption is not disabled"
        id = "CKV_AWS_78"
        supported_resources = ("AWS::CodeBuild::Project",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        # Only Fail if Artifact Type is S3 and EncryptionDisabled is True.
        artifact_type = ""
        encryption_disabled = False
        properties = conf.get("Properties")
        if properties:
            artifacts = properties.get("Artifacts")
            if artifacts and isinstance(artifacts, dict):
                if "Type" in artifacts.keys():
                    artifact_type = artifacts["Type"]
                if "EncryptionDisabled" in artifacts.keys():
                    encryption_disabled = artifacts["EncryptionDisabled"]
                if artifact_type == "S3" and encryption_disabled is True:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = CodeBuildProjectEncryption()
