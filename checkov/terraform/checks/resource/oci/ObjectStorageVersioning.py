from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ObjectStorageVersioning(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure OCI Object Storage has versioning enabled"
        id = "CKV_OCI_8"
        supported_resources = ['oci_objectstorage_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "versioning"

    def get_expected_value(self):
        return "Enabled"


check = ObjectStorageVersioning()
