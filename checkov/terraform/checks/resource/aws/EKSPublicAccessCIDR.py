from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

OPEN_CIDR_BLOCKS = ("0.0.0.0/0", "::/0", "0000:0000:0000:0000:0000:0000:0000:0000/0")  # nosec


class EKSPublicAccessCIDR(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Amazon EKS public endpoint not accessible to 0.0.0.0/0"
        id = "CKV_AWS_38"
        supported_resources = ('aws_eks_cluster',)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        """
            Looks for public_access_cidrs at aws_eks_cluster:
            https://www.terraform.io/docs/providers/aws/r/eks_cluster.html
        :param conf: aws_eks_cluster configuration
        :return: <CheckResult>
        """
        if "vpc_config" in conf.keys():
            if "endpoint_public_access" in conf["vpc_config"][0] and not conf["vpc_config"][0]["endpoint_public_access"][0]:
                return CheckResult.PASSED
            elif "public_access_cidrs" in conf["vpc_config"][0]:
                self.evaluated_keys = ['vpc_config/[0]/public_access_cidrs']
                cidrs = conf["vpc_config"][0]["public_access_cidrs"]
                if cidrs and isinstance(cidrs, list) and len(cidrs[0]):
                    cidr_values = cidrs[0]
                    if isinstance(cidr_values, str):
                        # resources rendered from for_each hold a single range as a plain string
                        cidr_values = [cidr_values]
                    if not any(cidr in OPEN_CIDR_BLOCKS for cidr in cidr_values):
                        return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = EKSPublicAccessCIDR()
