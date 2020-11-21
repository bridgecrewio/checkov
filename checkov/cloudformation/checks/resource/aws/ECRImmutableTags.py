from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ECRImmutableTags(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure ECR Image Tags are immutable"
        id = "CKV_AWS_51"
        supported_resources = ["AWS::ECR::Repository"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "Properties/ImageTagMutability"

    def get_expected_value(self):
        return "IMMUTABLE"

check = ECRImmutableTags()
