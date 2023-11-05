from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from checkov.common.checks_infra.extensions.iam_action_expansion import IamActionExpansion
from checkov.common.models.enums import GraphCheckExtension

if TYPE_CHECKING:
    from typing_extensions import Self

logger = logging.getLogger(__name__)


class GraphCheckExtensionsRegistry:
    _instance = None  # noqa: CCE003  # singleton

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.extensions = {
                IamActionExpansion.name: IamActionExpansion(),
            }

        return cls._instance

    def run(self, extensions: list[GraphCheckExtension], vertex_data: dict[str, Any]) -> dict[str, Any]:
        for extension in extensions:
            if extension not in self.extensions:
                logger.info(f"Extension {extension} doesn't exist")
                continue

            vertex_data = self.extensions[extension].extend(vertex_data=vertex_data)

        return vertex_data
