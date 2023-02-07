from __future__ import annotations

import json
import logging
from abc import abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from checkov.ansible.checks.registry import registry
from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckResult

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckCategories


class BaseAnsibleTaskCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: Iterable[CheckCategories],
        supported_modules: Iterable[str],
        block_type: str,
        guideline: str | None = None,
        path: str | None = None,
    ) -> None:
        supported_entities = [
            entity
            for module in supported_modules
            for entity in (
                f'[].tasks[?"{module}" != null][]',
                f'[?"{module}" != null][]',
                f'[].tasks[].block[?"{module}" != null][]',
                f'[].block[?"{module}" != null][]',
            )
        ]

        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
            guideline=guideline,
        )

        self.entity_conf: dict[str, Any]  # stores the complete entity configuration
        self.path = path
        self.supported_modules = supported_modules

        registry.register(self)

    def scan_entity_conf(  # type:ignore[override]  # multi_signature decorator is problematic
        self, conf: dict[str, Any], entity_type: str
    ) -> tuple[CheckResult, dict[str, Any]]:
        self.entity_type = entity_type
        self.entity_conf = conf

        module_conf = next((conf[module] for module in self.supported_modules if module in conf), None)
        if not module_conf:
            # this should actually never happen, but better to be safe, than sorry
            logging.info(f"Failed to find supported module {self.supported_modules} in {json.dumps(conf)}")
            return CheckResult.UNKNOWN, conf

        return self.scan_conf(module_conf)

    @abstractmethod
    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        pass
