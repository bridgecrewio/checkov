from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GoogleComputeBlockProjectSSH(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure 'Block Project-wide SSH keys' is enabled for VM instances"
        id = "CKV_GCP_32"
        supported_resources = ['google_compute_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'metadata/[0]/block-project-ssh-keys/[0]'


check = GoogleComputeBlockProjectSSH()
