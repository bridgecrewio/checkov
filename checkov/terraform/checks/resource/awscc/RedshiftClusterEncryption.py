from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RedshiftClusterEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Redshift clusters are encrypted"
        id = "CKV_AWS_64"
        supported_resources = ("awscc_redshift_cluster",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encrypted"

    def get_expected_value(self):
        return True


check = RedshiftClusterEncryption()
