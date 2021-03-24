from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class ReleaseChannel(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the GKE Release Channel is set"
        id = "CKV_GCP_70"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'release_channel/[0]/channel'

    def get_expected_values(self):
        return [ANY_VALUE]


check = ReleaseChannel()
