from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class PathSchemeDefineHTTP(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        # https://learning.postman.com/docs/api-governance/api-definition/openapi2/#schemes-of-the-operation-have-http-scheme-defined
        id = "CKV_OPENAPI_7"
        name = "Ensure that the path scheme does not support unencrypted HTTP connection where all transmissions " \
               "are open to interception- version 2.0 files"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ['security']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_openapi_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        paths = conf.get("paths", {})
        if not paths or not isinstance(paths, dict):
            return CheckResult.UNKNOWN, conf

        for path, http_method in paths.items():
            if self.is_start_end_line(path) or not http_method or not isinstance(http_method, dict):
                continue
            for op_name, op_val in http_method.items():
                if self.is_start_end_line(op_name):
                    continue
                if not isinstance(op_val, dict):
                    continue
                schemes = op_val.get('schemes')
                if schemes and 'http' in schemes:
                    return CheckResult.FAILED, conf
            # If the schemes is not included, the default scheme to be used is the one used to access the Swagger
            # definition itself, in which case the current check is not relevant.

        return CheckResult.PASSED, conf


check = PathSchemeDefineHTTP()
