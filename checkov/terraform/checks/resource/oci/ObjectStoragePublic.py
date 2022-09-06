from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class ObjectStoragePublic(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure OCI Object Storage is not Public"
        id = "CKV_OCI_10"
        supported_resources = ['oci_objectstorage_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "access_type"

    def get_forbidden_values(self):
        return ["ObjectRead", "ObjectReadWithoutList"]


check = ObjectStoragePublic()
