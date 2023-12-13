from __future__ import annotations

from typing import Any

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.data_structures_utils import find_in_dict


class AppServiceHttps20Enabled(BaseResourceCheck):
    # apiVersion = 2018-11-01 - http20Enabled is a string
    # apiVersion > 2020-10-01  - http20Enabled is a boolean
    def __init__(self) -> None:
        name = "Ensure that 'HTTP Version' is the latest if used to run the web app"
        id = "CKV_AZURE_18"
        supported_resources = ("Microsoft.Web/sites",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        http_20_enabled = find_in_dict(conf, "properties/siteConfig/http20Enabled")
        if http_20_enabled and "apiVersion" in conf:
            if conf["apiVersion"] == "2018-11-01":
                if isinstance(http_20_enabled, str) and str(http_20_enabled).lower() == "true":
                    return CheckResult.PASSED
            elif isinstance(http_20_enabled, bool) and http_20_enabled:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = AppServiceHttps20Enabled()
