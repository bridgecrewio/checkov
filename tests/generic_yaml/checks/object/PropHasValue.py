from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.yaml_doc.base_yaml_check import BaseYamlCheck
from checkov.yaml_doc.enums import BlockType


class PropHasValue(BaseYamlCheck):
    def __init__(self):
        name = (
            "Ensure that a foo object has a property named prop with a value of value"
        )
        id = "CKV_FOO_1"
        categories = [CheckCategories.CONVENTION]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["foo"],
            block_type=BlockType.OBJECT,
        )

    def scan_entity_conf(self, conf, entity_type):
        if "prop" in conf and conf["prop"] == "value":
            return CheckResult.PASSED
        return CheckResult.FAILED


check = PropHasValue()
