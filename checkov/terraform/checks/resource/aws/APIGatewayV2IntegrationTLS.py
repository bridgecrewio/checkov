from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class APIGatewayV2IntegrationTLS(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure API Gateway V2 private integrations use HTTPS via tls_config"
        id = "CKV_AWS_396"
        supported_resources = ["aws_apigatewayv2_integration"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # Only applies to VPC_LINK (private) integrations
        connection_type = conf.get("connection_type")
        if connection_type:
            if isinstance(connection_type, list):
                connection_type = connection_type[0]
        # Non-VPC_LINK integrations auto-pass
        if not connection_type or connection_type != "VPC_LINK":
            return CheckResult.PASSED

        self.evaluated_keys = ["tls_config/[0]/server_name_to_verify"]
        tls_config = conf.get("tls_config")
        if tls_config:
            if isinstance(tls_config, list):
                tls_config = tls_config[0]
            if isinstance(tls_config, dict):
                server_name = tls_config.get("server_name_to_verify")
                if server_name:
                    if isinstance(server_name, list):
                        server_name = server_name[0]
                    if BaseResourceCheck._is_variable_dependant(server_name):
                        return CheckResult.UNKNOWN
                    if isinstance(server_name, str) and server_name.strip():
                        return CheckResult.PASSED

        # FAIL if tls_config is absent or server_name_to_verify is empty
        return CheckResult.FAILED


check = APIGatewayV2IntegrationTLS()
