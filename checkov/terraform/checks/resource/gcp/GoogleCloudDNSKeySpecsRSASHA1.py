from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleCloudDNSKeySpecsRSASHA1(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that RSASHA1 is not used for the zone-signing and key-signing keys in Cloud DNS DNSSEC"
        id = "CKV_GCP_17"
        supported_resources = ["google_dns_managed_zone"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for DNSSEC key algorithm at dns_managed_zone:
            https://www.terraform.io/docs/providers/google/r/dns_managed_zone.html#algorithm
        :param conf: dns_managed_zone configuration
        :return: <CheckResult>
        """
        dnssec_configs = conf.get("dnssec_config")
        if dnssec_configs is None:
            return CheckResult.PASSED

        self.evaluated_keys = ["dnssec_config"]
        if not isinstance(dnssec_configs, list) or not dnssec_configs:
            return CheckResult.UNKNOWN

        dnssec_config = dnssec_configs[0]
        if not isinstance(dnssec_config, dict):
            return CheckResult.UNKNOWN

        default_key_specs = dnssec_config.get("default_key_specs")
        # Default algorithm is RSASHA256: https://cloud.google.com/dns/docs/dnssec-advanced#advanced-signing-options
        if default_key_specs is None:
            return CheckResult.PASSED
        if not isinstance(default_key_specs, list):
            return CheckResult.UNKNOWN

        has_unknown_key_specs = False
        for index, key_specs in enumerate(default_key_specs):
            if not isinstance(key_specs, dict):
                has_unknown_key_specs = True
                continue

            algorithm = key_specs.get("algorithm")
            if algorithm == ["rsasha1"]:
                self.evaluated_keys = [f"dnssec_config/[0]/default_key_specs/[{index}]/algorithm"]
                return CheckResult.FAILED
            if algorithm is not None and (
                not isinstance(algorithm, list)
                or len(algorithm) != 1
                or not isinstance(algorithm[0], str)
                or self._is_variable_dependant(algorithm[0])
            ):
                has_unknown_key_specs = True

        self.evaluated_keys = ["dnssec_config/[0]/default_key_specs"]
        if has_unknown_key_specs:
            return CheckResult.UNKNOWN

        return CheckResult.PASSED


check = GoogleCloudDNSKeySpecsRSASHA1()
