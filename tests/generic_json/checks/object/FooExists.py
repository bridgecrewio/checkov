from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.json_doc.base_json_check import BaseJsonCheck
from checkov.json_doc.enums import BlockType


class FooExists(BaseJsonCheck):
    def __init__(self):
        name = "Ensure that a foo object is present"
        id = "CKV_FOO_2"
        categories = [CheckCategories.CONVENTION]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT,
        )

    def scan_entity_conf(self, conf):
        if "foo" in conf:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = FooExists()
