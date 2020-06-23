from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GoogleCloudDNSSECEnabled(BaseResourceValueCheck):
    """
    Looks for DNSSEC state at dns_managed_zone:
    https://www.terraform.io/docs/providers/google/r/dns_managed_zone.html#state
    """

    def __init__(self):
        name = "Ensure that DNSSEC is enabled for Cloud DNS"
        id = "CKV_GCP_16"
        supported_resources = ["google_dns_managed_zone"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "dnssec_config/[0]/state"

    def get_expected_value(self):
        return "on"

    def get_expected_values(self):
        return [self.get_expected_value(), "transfer"]


check = GoogleCloudDNSSECEnabled()
