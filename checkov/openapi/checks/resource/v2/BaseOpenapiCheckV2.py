from __future__ import annotations

from typing import Iterable, Any
from abc import abstractmethod
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class BaseOpenapiCheckV2(BaseOpenapiCheck):
    def __init__(self, name: str, id: str, categories: Iterable[CheckCategories], supported_entities: Iterable[str],
                 block_type: str) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
        )

    @abstractmethod
    def scan_openapi_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        raise NotImplementedError()

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:  # type:ignore[override]
        if "swagger" in conf and conf.get("swagger") == '2.0':
            return self.scan_openapi_conf(conf, entity_type)
        return CheckResult.UNKNOWN, conf
