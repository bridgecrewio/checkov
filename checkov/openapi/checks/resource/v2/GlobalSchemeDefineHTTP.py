from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class GlobalSchemeDefineHTTP(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_18"
        name = "Ensure that global schemes use 'https' protocol instead of 'http'- version 2.0 files"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ['schemes']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_openapi_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        schemes = conf.get("schemes", [])
        if not schemes:
            # If the schemes is not included, the default scheme to be used is the one used to access the Swagger
            # definition itself, in which case the current check is not relevant.
            return CheckResult.UNKNOWN, conf
        if 'http' in schemes:
            return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf


check = GlobalSchemeDefineHTTP()
