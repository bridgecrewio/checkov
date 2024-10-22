from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.json_doc.base_json_check import BaseJsonCheck
from checkov.json_doc.enums import BlockType


class NoEvaluatedKey(BaseJsonCheck):
    def __init__(self):
        name = "Ensure that entire conf is returned for empty evaluated key"
        id = "CKV_RESULT_CONFIG_1"
        categories = [CheckCategories.CONVENTION]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=("*",),
            block_type=BlockType.DOCUMENT,
        )

    def scan_entity_conf(self, conf, entity_type):
        return CheckResult.PASSED


check = NoEvaluatedKey()
