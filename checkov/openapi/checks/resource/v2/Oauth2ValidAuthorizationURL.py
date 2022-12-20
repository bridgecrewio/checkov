from __future__ import annotations
import re

from typing import Any, Union, List
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2
from checkov.openapi.utils import VALID_URL_REGEX


class Oauth2ValidAuthorizationURL(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_19"
        name = "Ensure that the authorizationUrl field on implicit or authorizationCode fields on OAuth have a valid " \
               "URL - version 2.0 files"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ["securityDefinitions"]
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
            if self.is_start_end_line(auth_key):
                continue
            auth_type = auth_dict.get('type', '')
            if auth_type.lower() == 'oauth2':
                auth_flow = auth_dict.get('flow', '')
                if auth_flow in ['accessCode', 'implicit']:
                    auth_url = auth_dict.get('authorizationUrl', '')
                    if not re.match(VALID_URL_REGEX, auth_url):
                        return CheckResult.FAILED, auth_dict

        return CheckResult.PASSED, conf


check = Oauth2ValidAuthorizationURL()
