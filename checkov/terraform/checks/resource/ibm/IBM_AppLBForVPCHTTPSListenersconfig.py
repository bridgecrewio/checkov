from __future__ import annotations

import itertools
from typing import Any

from checkov.common.util.type_forcers import force_list

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class IBM_VirtualServersForVPCInstanceIPspoofingDisabled(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Application Load Balancer for VPC is configured with HTTPS Listeners"
        id = "CKV2_IBM_9"
        supported_resources = ("ibm_is_instance",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:

#         My code here

check = IBM_VirtualServersForVPCInstanceIPspoofingDisabled()
