from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.json.base_json_check import BaseJsonCheck
from checkov.json.enums import BlockType


class BarToggleIsTrue(BaseJsonCheck):
    def __init__(self):
        name = "A bar should have toggle set to true"
        id = "CKV_BAR_1"
        categories = [CheckCategories.CONVENTION]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["bar"],
            block_type=BlockType.ARRAY
        )

    def scan_entity_conf(self, conf):
        if "toggle" in conf and conf["toggle"]:
            return CheckResult.PASSED, conf
        return CheckResult.FAILED, conf


check = BarToggleIsTrue()
