from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class GoogleComputeIPForward(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that IP forwarding is not enabled on Instances"
        id = "CKV_GCP_36"
        supported_resources = ['google_compute_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'can_ip_forward'

    def get_forbidden_values(self):
        return [True]

    def get_excluded_key(self):
        return "name"

    def check_excluded_condition(self, value):
        return value.startswith('gke-')


check = GoogleComputeIPForward()
