from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.yaml_doc.base_yaml_check import BaseYamlCheck
from checkov.yaml_doc.enums import BlockType


class ValueIsAtLeastTwo(BaseYamlCheck):
    def __init__(self):
        name = "Ensure that an object has a value >= 2"
        id = "CKV_COMPLEX_1"
        categories = [CheckCategories.CONVENTION]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["prop_is_array_of_object"],
            block_type=BlockType.ARRAY,
            path="array_of_objects"
        )

    def scan_entity_conf(self, conf, entity_type):
        for obj in conf:
            if obj["value"] < 2:
                return CheckResult.FAILED, obj
        return CheckResult.PASSED


check = ValueIsAtLeastTwo()
