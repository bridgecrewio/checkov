from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class EKSPlatformVersion(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 CA-9(1), NIST.800-53.r5 CM-2, NIST.800-53.r5 SI-2, NIST.800-53.r5 SI-2(2),
        NIST.800-53.r5 SI-2(4), NIST.800-53.r5 SI-2(5)
        EKS clusters should run on a supported Kubernetes version
        """
        name = "Ensure EKS clusters run on a supported Kubernetes version"
        id = "CKV_AWS_339"
        supported_resources = ("aws_eks_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "version"

    def get_expected_values(self) -> list[Any]:
        # https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html
        return ["1.25", "1.26", "1.27", "1.28", "1.29", "1.30", "1.31", "1.32"]


check = EKSPlatformVersion()
