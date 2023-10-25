from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.yaml_doc.base_yaml_check import BaseYamlCheck
from checkov.yaml_doc.enums import BlockType


class BarAndBazToggleIsTrue(BaseYamlCheck):
    def __init__(self):
        name = "A bar should have toggle set to true"
        id = "CKV_BARBAZ_1"
        categories = [CheckCategories.CONVENTION]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["bar", "baz"],
            block_type=BlockType.ARRAY
        )

    def scan_entity_conf(self, conf, entity_type):
        if "toggle" in conf and conf["toggle"]:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = BarAndBazToggleIsTrue()
