from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class VPCSecurityGroupAllowAll(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure security group does not contain allow-all rules."
        id = "CKV_YC_19"
        categories = (CheckCategories.GENERAL_SECURITY,)
        supported_resources = ("yandex_vpc_security_group",)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "ingress" in conf.keys():
            cidr_block = conf["ingress"][0]["v4_cidr_blocks"]
            self.evaluated_keys = ["ingress/[0]/v4_cidr_blocks"]
            for cidr in cidr_block[0]:
                if cidr == "0.0.0.0/0":
                    if "port" in conf["ingress"][0].keys():
                        if conf["ingress"][0]["port"][0] == -1:
                            return CheckResult.FAILED
                        return CheckResult.PASSED
                    if "from_port" not in conf["ingress"][0].keys() and "to_port" not in conf["ingress"][0].keys():
                        return CheckResult.FAILED
                    if conf["ingress"][0]["from_port"][0] == 0 and conf["ingress"][0]["to_port"][0] == 65535:
                        return CheckResult.FAILED
        return CheckResult.PASSED


scanner = VPCSecurityGroupAllowAll()
