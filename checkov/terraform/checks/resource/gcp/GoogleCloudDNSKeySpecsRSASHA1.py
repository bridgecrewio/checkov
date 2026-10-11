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
        dnssec_configs = conf.get("dnssec_config")
        if not dnssec_configs:
            return CheckResult.PASSED

        has_unknown_key_specs = False
        self.evaluated_keys = ["dnssec_config"]
        for dnssec_config in dnssec_configs:
            if not isinstance(dnssec_config, dict):
                has_unknown_key_specs = True
                continue

            default_key_specs = dnssec_config.get("default_key_specs")
            if default_key_specs is None:
                continue
            if not isinstance(default_key_specs, list):
                has_unknown_key_specs = True
                continue

            for index, key_specs in enumerate(default_key_specs):
                if not isinstance(key_specs, dict):
                    has_unknown_key_specs = True
                    continue
                if key_specs.get("algorithm") == ["rsasha1"]:
                    self.evaluated_keys = [f"dnssec_config/[0]/default_key_specs/[{index}]/algorithm"]
                    return CheckResult.FAILED
                algorithm = key_specs.get("algorithm")
                if algorithm is not None and not isinstance(algorithm, list):
                    has_unknown_key_specs = True

        self.evaluated_keys = ["dnssec_config/[0]/default_key_specs"]
        if has_unknown_key_specs:
            return CheckResult.UNKNOWN
        return CheckResult.PASSED


check = GoogleCloudDNSKeySpecsRSASHA1()
