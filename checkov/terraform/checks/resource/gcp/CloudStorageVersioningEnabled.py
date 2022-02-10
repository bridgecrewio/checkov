from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class CloudStorageVersioningEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Cloud storage has versioning enabled"
        id = "CKV_GCP_78"
        supported_resources = ['google_storage_bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "versioning/[0]/enabled"


check = CloudStorageVersioningEnabled()
