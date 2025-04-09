from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ECSServiceFargateLatest(BaseResourceCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 SI-2, NIST.800-53.r5 SI-2(2), NIST.800-53.r5 SI-2(4), NIST.800-53.r5 SI-2(5)
        ECS Fargate services should run on the latest Fargate platform version
        """
        name = "Ensure ECS Fargate services run on the latest Fargate platform version"
        id = "CKV_AWS_332"
        supported_resources = ("aws_ecs_service",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        launch_type = conf.get("launch_type")
        if launch_type and isinstance(launch_type, list) and launch_type[0] == "FARGATE":
            platform_version = conf.get("platform_version")
            if platform_version and isinstance(platform_version, list) and platform_version[0] != "LATEST":
                return CheckResult.FAILED
            return CheckResult.PASSED

        return CheckResult.UNKNOWN

    def get_evaluated_keys(self) -> List[str]:
        return ["launch_type", "platform_version"]


check = ECSServiceFargateLatest()
