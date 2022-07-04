from operator import contains
from checkov.circleci_pipelines.base_circleci_pipelines_check import BaseCircleCIPipelinesCheck
from checkov.common.models.enums import CheckResult
from checkov.yaml_doc.enums import BlockType


class ImageReferenceHashVersion(BaseCircleCIPipelinesCheck):
    def __init__(self):
        name = "Ensure the pipeline image version is referenced via hash not arbitrary tag."
        id = "CKV_CIRCLECIPIPELINES_2"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=['jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}']
        )

    def scan_entity_conf(self, conf):
        if not isinstance(conf, dict):
            return
        image = conf.get("image", None)
        if not image:
            return
        if isinstance(image, str):
              if "@" in image:
                return CheckResult.PASSED, conf

        return CheckResult.FAILED, conf


check = ImageReferenceHashVersion()
