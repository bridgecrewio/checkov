from __future__ import annotations

from typing import Any

from checkov.azure_pipelines.checks.base_azure_pipelines_check import BaseAzurePipelinesCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.yaml_doc.enums import BlockType


class ContainerLatestTag(BaseAzurePipelinesCheck):
    def __init__(self) -> None:
        name = "Ensure container job uses a non latest version tag"
        id = "CKV_AZUREPIPELINES_1"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.SUPPLY_CHAIN,),
            supported_entities=("jobs", "stages[].jobs[]"),
            block_type=BlockType.ARRAY,
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        container = conf.get("container")
        if container and isinstance(container, dict):
            container = container.get('image')
        if container and isinstance(container, str):
            if ":" in container:
                # some image tag
                if container.split(":")[1] == "latest":
                    # latest image tag
                    return CheckResult.FAILED, conf
            elif "@" not in container:
                # no image tag
                return CheckResult.FAILED, conf

            # image tag is either not latest or a digest
            return CheckResult.PASSED, conf

        return CheckResult.UNKNOWN, conf


check = ContainerLatestTag()
