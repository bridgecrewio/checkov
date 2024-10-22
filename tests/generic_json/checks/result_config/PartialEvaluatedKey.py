from typing import List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.json_doc.base_json_check import BaseJsonCheck
from checkov.json_doc.enums import BlockType


class PartialEvaluatedKey(BaseJsonCheck):
    def __init__(self):
        name = "Ensure that the closest parent configuration block is returned for an evaluated key path that points" \
               "to a string"
        id = "CKV_RESULT_CONFIG_2"
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

    def get_evaluated_keys(self) -> List[str]:
        return ['required_pull_request_reviews/dismissal_restrictions/users']


check = PartialEvaluatedKey()
