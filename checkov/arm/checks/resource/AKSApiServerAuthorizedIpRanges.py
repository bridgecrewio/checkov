from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class AKSApiServerAuthorizedIpRanges(BaseResourceCheck):
    def __init__(self) -> None:
        # apiVersion 2017-08-03 and 2018-03-31 = Fail - No authorized IP range available
        # apiVersion 2019-02-01, 2019-04-01, 2019-06-01 - Preview
        # apiversion 2019-08-01 and greater are fully supported
        name = "Ensure AKS has an API Server Authorized IP Ranges enabled"
        id = "CKV_AZURE_6"
        supported_resources = ('Microsoft.ContainerService/managedClusters',)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "apiVersion" in conf:
            if conf["apiVersion"] in ["2017-08-31", "2018-03-31"]:
                # ApiServerAuthorizedIpRanges not supported in these API versions
                return CheckResult.FAILED
            elif conf["apiVersion"] in ["2019-02-01", "2019-04-01", "2019-06-01"]:
                # apiServerAuthorizedIPRanges in Preview in these API versions
                if "properties" in conf:
                    if "apiServerAuthorizedIPRanges" in conf["properties"]:
                        if conf["properties"]["apiServerAuthorizedIPRanges"]:
                            return CheckResult.PASSED
            else:
                # ApiServerAuthorizedIpRanges fully supported in all future API versions
                properties = conf.get('properties')
                if not properties or not isinstance(properties, dict):
                    return CheckResult.FAILED
                api_server_access_profile = properties.get('apiServerAccessProfile')
                if not api_server_access_profile:
                    return CheckResult.FAILED
                authorized_ip_ranges = api_server_access_profile.get('authorizedIPRanges')
                if authorized_ip_ranges:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = AKSApiServerAuthorizedIpRanges()
