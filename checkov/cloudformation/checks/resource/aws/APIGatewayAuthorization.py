from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class APIGatewayAuthorization(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure there is no open access to back-end resources through API"
        id = "CKV_AWS_59"
        supported_resources = ('AWS::ApiGateway::Method',)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if 'Properties' in conf.keys():
            if 'HttpMethod' in conf['Properties'].keys() and 'AuthorizationType' in conf['Properties'].keys():
                if conf['Properties']['HttpMethod'] != "OPTIONS" and conf['Properties']['AuthorizationType'] == "NONE":
                    if 'ApiKeyRequired' not in conf['Properties'].keys() or conf['Properties']['ApiKeyRequired'] is False:
                        return CheckResult.FAILED
        return CheckResult.PASSED


check = APIGatewayAuthorization()
