from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.yaml_doc.base_yaml_check import BaseYamlCheck
from checkov.yaml_doc.enums import BlockType


class FooExists(BaseYamlCheck):
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

    def scan_entity_conf(self, conf, entity_type):
        if "foo" in conf:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = FooExists()
