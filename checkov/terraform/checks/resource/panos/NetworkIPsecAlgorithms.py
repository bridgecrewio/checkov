from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class NetworkIPsecAlgorithms(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure IPsec profiles do not specify use of insecure encryption algorithms"
        id = "CKV_PAN_11"
        supported_resources = ('panos_ipsec_crypto_profile', 'panos_panorama_ipsec_crypto_profile')
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # Check there are encryptions defined in the resource
        if 'encryptions' in conf:

            # Report the area of evaluation
            self.evaluated_keys = ['encryptions']

            # Get all the algorithms
            algorithms = conf['encryptions']

            # Iterate over each algorithm, as multiple can be defined in "encryptions"
            for algo in algorithms:

                # Check for insecure algorithms, including null as a string (not a null value)
                if algo[0] in ('des', '3des', 'aes-128-cbc', 'aes-192-cbc', 'aes-256-cbc', 'null'):

                    # Fail if any insecure algorithms are defined for use
                    return CheckResult.FAILED

            # If no fails have been found, this is a pass
            return CheckResult.PASSED

        # If the mandatory "encryptions" attribute is not defined, this is not valid, and will fail during Terraform plan stage, and should therefore be a fail
        return CheckResult.FAILED


check = NetworkIPsecAlgorithms()
