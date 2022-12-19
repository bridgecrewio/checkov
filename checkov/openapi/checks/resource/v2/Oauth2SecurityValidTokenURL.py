from __future__ import annotations
import re

from typing import Any, Union, List
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2

VALID_URL_REGEX = re.compile(r'^(https?):\/\/(-\.)?([^\s\/?\.#-]+([-\.\/])?)+(\/[^\s]*)?$')

class Oauth2SecurityValidTokenURL(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_9"
        name = "Ensure that oAuth2 security definition flow requires a valid URL in the tokenUrl field - version 2.0 " \
               "files "
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
            if auth_type.lower() == 'oauth2':
                token_url = auth_dict.get('tokenUrl', '')
                if not re.match(VALID_URL_REGEX, token_url):
                    return CheckResult.FAILED, auth_dict

        return CheckResult.PASSED, conf


check = Oauth2SecurityValidTokenURL()
