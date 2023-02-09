from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DocDBEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure DocDB is encrypted at rest (default is unencrypted)"
        id = "CKV_AWS_74"
        supported_resources = ("AWS::DocDB::DBCluster",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/StorageEncrypted"


check = DocDBEncryption()
