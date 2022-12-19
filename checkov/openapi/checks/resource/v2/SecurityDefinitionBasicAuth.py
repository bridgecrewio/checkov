from __future__ import annotations

from typing import Any, Union, List
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class Oauth2SecurityDefinitionImplicitFlow(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_13"
        name = "Ensure security definitions do not use basic auth - version 2.0 files"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ["securityDefinitions"]
        self.irrelevant_keys = ['__startline__', '__endline__']
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_resources,
            block_type=BlockType.DOCUMENT,
        )

    def scan_openapi_conf(  # type:ignore[override]
            self, conf: dict[str, Any], entity_type: str
    ) -> tuple[CheckResult, Union[dict[str, Any], List[Any]]]:
        security_definitions = conf.get('securityDefinitions', {}) or {}

        for auth_key, auth_dict in security_definitions.items():
            if auth_key in self.irrelevant_keys:
                continue
            auth_type = auth_dict.get('type')
            if auth_type.lower() == 'basic':
                return CheckResult.FAILED, auth_dict

        return CheckResult.PASSED, conf


check = Oauth2SecurityDefinitionImplicitFlow()
