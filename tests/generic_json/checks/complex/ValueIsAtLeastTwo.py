from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.json_doc.base_json_check import BaseJsonCheck
from checkov.json_doc.enums import BlockType


class ValueIsAtLeastTwo(BaseJsonCheck):
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

    def scan_entity_conf(self, conf):
        for obj in conf:
            if obj["value"] < 2:
                return CheckResult.FAILED, obj
        return CheckResult.PASSED


check = ValueIsAtLeastTwo()
