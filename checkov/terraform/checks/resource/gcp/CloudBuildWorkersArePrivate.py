from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class CloudBuildWorkersArePrivate(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure Cloud build workers are private"
        id = "CKV_GCP_86"
        supported_resources = ['google_cloudbuild_worker_pool']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "worker_config/[0]/no_external_ip"


check = CloudBuildWorkersArePrivate()
