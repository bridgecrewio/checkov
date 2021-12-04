from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck

strongCiphers = (
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_RSA_WITH_AES_128_GCM_SHA256",
)


class KubeletCryptographicCiphers(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 4.2.13
        id = "CKV_K8S_151"
        name = "Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kubelet" in conf["command"]:
                for command in conf["command"]:
                    if command.startswith("--tls-cipher-suites"):
                        value = command.split("=")[1]
                        ciphers = value.split(",")
                        for cipher in ciphers:
                            if cipher not in strongCiphers:
                                return CheckResult.FAILED

        return CheckResult.PASSED


check = KubeletCryptographicCiphers()
