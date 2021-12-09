
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SpaceBucketVersioning(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the Spaces bucket has versioning enabled"
        id = "CKV_DIO_1"
        supported_resources = ['digitalocean_spaces_bucket']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        self.evaluated_keys = ["versioning/[0]/enabled"]
        return "versioning/[0]/enabled"


check = SpaceBucketVersioning()
