from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleCloudDNSSECEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that DNSSEC is enabled for Cloud DNS"
        id = "CKV_GCP_16"
        supported_resources = ["google_dns_managed_zone"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for DNSSEC state at dns_managed_zone:
            https://www.terraform.io/docs/providers/google/r/dns_managed_zone.html#state
        :param conf: dns_managed_zone configuration
        :return: <CheckResult>
        """
        if "dnssec_config" in conf.keys():
            dnssec_config = conf["dnssec_config"][0]
            if "state" in dnssec_config and dnssec_config["state"] != ["off"]:
                return CheckResult.PASSED

        return CheckResult.FAILED


check = GoogleCloudDNSSECEnabled()
