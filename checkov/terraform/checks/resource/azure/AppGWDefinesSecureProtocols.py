from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

BAD_CIPHERS = {
    "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
    "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_DHE_RSA_WITH_AES_256_CBC_SHA",
    "TLS_DHE_RSA_WITH_AES_128_CBC_SHA",
    "TLS_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_RSA_WITH_AES_256_CBC_SHA256",
    "TLS_RSA_WITH_AES_128_CBC_SHA256",
    "TLS_RSA_WITH_AES_256_CBC_SHA",
    "TLS_RSA_WITH_AES_128_CBC_SHA",
    "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384 ",
    "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
    "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
    "TLS_DHE_DSS_WITH_AES_256_CBC_SHA256",
    "TLS_DHE_DSS_WITH_AES_128_CBC_SHA256 ",
    "TLS_DHE_DSS_WITH_AES_256_CBC_SHA",
    "TLS_DHE_DSS_WITH_AES_128_CBC_SHA",
    "TLS_RSA_WITH_3DES_EDE_CBC_SHA",
    "TLS_DHE_DSS_WITH_3DES_EDE_CBC_SHA",
}
PROTOCOL_VERSIONS = {"TLSv1_2", "TLSv1_3"}


class AppGWDefinesSecureProtocols(BaseResourceCheck):
    def __init__(self) -> None:
        """
        https://azure.github.io/PSRule.Rules.Azure/en/rules/Azure.AppGw.SSLPolicy/

        """
        name = "Ensure Application Gateway defines secure protocols for in transit communication"
        id = "CKV_AZURE_218"
        supported_resources = ("azurerm_application_gateway",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        ssl_policy = conf.get("ssl_policy")
        if ssl_policy and isinstance(ssl_policy, list):
            ssl_policy = ssl_policy[0]
            policy_type = ssl_policy.get("policy_type")
            if policy_type and isinstance(policy_type, list):
                if policy_type[0] != "Predefined":
                    protocol_version = ssl_policy.get("min_protocol_version")
                    if (
                        protocol_version
                        and isinstance(protocol_version, list)
                        and protocol_version[0] in PROTOCOL_VERSIONS
                    ):
                        ciphers = ssl_policy.get("cipher_suites")
                        if ciphers and isinstance(ciphers, list) and any(cipher in BAD_CIPHERS for cipher in ciphers[0]):
                            self.evaluated_keys = ["ssl_policy/[0]/cipher_suites"]
                            return CheckResult.FAILED
                        return CheckResult.PASSED

                policy_name = ssl_policy.get("policy_name")
                if policy_name and isinstance(policy_name, list) and policy_name[0] == "AppGwSslPolicy20220101S":
                    return CheckResult.PASSED
                self.evaluated_keys = ["ssl_policy/[0]/policy_name"]
                return CheckResult.FAILED

        self.evaluated_keys = ["ssl_policy"]
        return CheckResult.FAILED


check = AppGWDefinesSecureProtocols()
