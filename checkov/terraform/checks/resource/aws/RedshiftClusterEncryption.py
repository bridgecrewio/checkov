from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class RedshiftClusterEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the Redshift cluster is securely encrypted at rest"
        id = "CKV_AWS_64"
        supported_resources = ['aws_redshift_cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encrypted"


check = RedshiftClusterEncryption()
