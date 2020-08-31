from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DocDBEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure DocDB is encrypted at rest (default is unencrypted)"
        id = "CKV_AWS_74"
        supported_resources = ['aws_docdb_cluster', 'aws_docdb_cluster_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "storage_encrypted"


check = DocDBEncryption()
