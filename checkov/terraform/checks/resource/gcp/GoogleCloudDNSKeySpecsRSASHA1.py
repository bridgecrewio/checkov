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
        if "dnssec_config" in conf.keys():
            dnssec_config = conf["dnssec_config"][0]
            self.evaluated_keys = ['dnssec_config']
            # default algo RSASHA256 as per the documentation:
            # https://cloud.google.com/dns/docs/dnssec-advanced#advanced-signing-options
            if "default_key_specs" in dnssec_config:
                for default_key_specs in dnssec_config["default_key_specs"]:
                    if "algorithm" in default_key_specs and default_key_specs["algorithm"] == ["rsasha1"]:
                        self.evaluated_keys = [f'dnssec_config/[0]/default_key_specs/'
                                               f'[{dnssec_config["default_key_specs"].index(default_key_specs)}]/'
                                               f'algorithm']
                        return CheckResult.FAILED
                self.evaluated_keys = ['dnssec_config/[0]/default_key_specs']
        return CheckResult.PASSED


check = GoogleCloudDNSKeySpecsRSASHA1()
