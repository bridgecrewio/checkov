from abc import abstractmethod
from collections.abc import Iterable
from typing import List, Dict, Any, Optional

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.terraform.registry import terraform_registry


class BaseTerraformBlockCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_blocks: "Iterable[str]",
        guideline: Optional[str] = None
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_blocks,
            block_type="terraform",
            guideline=guideline,
        )
        self.supported_blocks = supported_blocks
        terraform_registry.register(self)

    def scan_entity_conf(self, conf: Dict[str, List[Any]], entity_type: str) -> CheckResult:
        return self.scan_terraform_block_conf(conf)

    @abstractmethod
    def scan_terraform_block_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        raise NotImplementedError()
