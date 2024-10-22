from __future__ import annotations
from typing import Any

from checkov.circleci_pipelines.base_circleci_pipelines_check import BaseCircleCIPipelinesCheck
from checkov.common.models.enums import CheckResult
from checkov.yaml_doc.enums import BlockType


class PreventVolatileOrbs(BaseCircleCIPipelinesCheck):
    def __init__(self) -> None:
        name = "Ensure unversioned volatile orbs are not used."
        id = "CKV_CIRCLECIPIPELINES_4"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=("orbs.{orbs: @}",)
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        for orb in conf.values():
            if isinstance(orb, str):
                # Special __ vars show up in this dict too.
                if "@volitile" in orb:
                    # We only get one return per orb: section, regardless of how many orbs.
                    # Potentially more JMEpath reflection-foo can resolve this so we end up with a call to scan_entity_conf per orb.
                    return CheckResult.FAILED, conf

        return CheckResult.PASSED, conf


check = PreventVolatileOrbs()
