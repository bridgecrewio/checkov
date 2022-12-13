from __future__ import annotations

import re
from typing import Iterable
from typing import Any

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories
from checkov.github.dal import CKV_METADATA
from checkov.github.registry import registry


HTTP = re.compile("^http://")


class BaseGithubCheck(BaseCheck):
    def __init__(self, name: str, id: str, categories: Iterable[CheckCategories], supported_entities: Iterable[str],
                 block_type: str, path: str | None = None, guideline: str | None = None) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
            guideline=guideline,
        )
        self.path = path
        registry.register(self)

    @staticmethod
    def resolve_ckv_metadata_conf(conf: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        if isinstance(conf, list) and conf:
            ckv_metadata = conf[-1]
            new_conf = conf[:-1]
            return ckv_metadata, new_conf
        elif isinstance(conf, dict):
            ckv_metadata = conf.get(CKV_METADATA)
            if ckv_metadata:
                new_conf = conf.copy()
                del new_conf[CKV_METADATA]
                return ckv_metadata, new_conf
        return {}, conf
