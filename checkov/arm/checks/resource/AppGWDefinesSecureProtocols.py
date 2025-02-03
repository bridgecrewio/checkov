from __future__ import annotations
from typing import Any, List
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck

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
        supported_resources = ("Microsoft.Network/applicationGateways",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name,
                         id=id,
                         categories=categories,
                         supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        sslPolicy = conf["properties"].get("sslPolicy")
        if sslPolicy and isinstance(sslPolicy, dict):
            policyType = sslPolicy.get("policyType")
            if policyType != "Predefined":
                protocolversion = sslPolicy.get("minProtocolVersion")
                if (
                        protocolversion and isinstance(protocolversion, str)
                        and protocolversion in PROTOCOL_VERSIONS
                ):
                    ciphers = sslPolicy.get("cipherSuites")
                    if ciphers and isinstance(ciphers, list) and any(cipher in BAD_CIPHERS for cipher in ciphers):
                        return CheckResult.FAILED
                    return CheckResult.PASSED

            policyName = sslPolicy.get("policyName")
            if policyName == "AppGwSslPolicy20220101S":
                return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["properties/sslPolicy", "properties/sslPolicy/policyType", "properties/sslPolicy/minProtocolVersion",
                "properties/sslPolicy/cipherSuites"]


check = AppGWDefinesSecureProtocols()
