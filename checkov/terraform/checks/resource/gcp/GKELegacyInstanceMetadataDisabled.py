from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_float
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GKELegacyInstanceMetadataDisabled(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure legacy Compute Engine instance metadata APIs are Disabled"
        id = "CKV_GCP_67"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        looks for min_master_version =1.12 which ensures that legacy metadata endpoints are disabled
        https://www.terraform.io/docs/providers/google/r/compute_ssl_policy.html
        :param conf: google_container_cluster configuration
        :return: <CheckResult>
        """
        if 'min_master_version' in conf:
            min_master_version = force_float(conf.get('min_master_version')[0])
            if min_master_version and min_master_version >= 1.12:
                return CheckResult.PASSED

        return CheckResult.FAILED

    def get_inspected_key(self):
        return 'min_master_version'

    def get_expected_value(self):
        return "1.12"


check = GKELegacyInstanceMetadataDisabled()
