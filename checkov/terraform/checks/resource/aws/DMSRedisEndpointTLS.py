from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DMSRedisEndpointTLS(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure DMS Redis endpoint has TLS enabled"
        id = "CKV_AWS_397"
        supported_resources = ["aws_dms_endpoint"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # Only applies to Redis endpoints
        engine_name = conf.get("engine_name")
        if engine_name:
            if isinstance(engine_name, list):
                engine_name = engine_name[0]
        if not engine_name or engine_name != "redis":
            return CheckResult.PASSED

        self.evaluated_keys = ["redis_settings/[0]/ssl_security_protocol"]
        redis_settings = conf.get("redis_settings")
        if redis_settings:
            if isinstance(redis_settings, list):
                redis_settings = redis_settings[0]
            if isinstance(redis_settings, dict):
                ssl_protocol = redis_settings.get("ssl_security_protocol")
                if ssl_protocol:
                    if isinstance(ssl_protocol, list):
                        ssl_protocol = ssl_protocol[0]
                    if BaseResourceCheck._is_variable_dependant(ssl_protocol):
                        return CheckResult.UNKNOWN
                    if isinstance(ssl_protocol, str) and ssl_protocol.lower() == "plaintext":
                        return CheckResult.FAILED
                    # Explicit ssl-encryption passes
                    if isinstance(ssl_protocol, str) and ssl_protocol.lower() == "ssl-encryption":
                        return CheckResult.PASSED

        # If redis_settings is absent or ssl_security_protocol is absent,
        # AWS defaults to ssl-encryption, so PASS
        return CheckResult.PASSED


check = DMSRedisEndpointTLS()
