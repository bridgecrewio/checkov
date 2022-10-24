from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ObjectStorageEmitEvents(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure OCI Object Storage bucket can emit object events"
        id = "CKV_OCI_7"
        supported_resources = ['oci_objectstorage_bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "object_events_enabled"

    def get_expected_value(self):
        return True


check = ObjectStorageEmitEvents()
