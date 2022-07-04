from asyncio.log import logger
from checkov.circleci_pipelines.base_circleci_pipelines_check import BaseCircleCIPipelinesCheck
from checkov.common.models.enums import CheckResult
from checkov.yaml_doc.enums import BlockType

class PreventDevelopmentOrbs(BaseCircleCIPipelinesCheck):
    def __init__(self):
        name = "Ensure unversioned volatile orbs are not used."
        id = "CKV_CIRCLECIPIPELINES_4"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=['orbs']
        )

    def scan_entity_conf(self, conf):
        if isinstance(conf, str):
            if "@volatile" in conf:
                return CheckResult.FAILED, conf
        else:
                return CheckResult.PASSED, conf
        return CheckResult.PASSED, conf


check = PreventDevelopmentOrbs()
