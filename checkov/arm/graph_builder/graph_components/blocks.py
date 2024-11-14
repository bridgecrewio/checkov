from __future__ import annotations

from typing import Any

from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.graph.graph_builder.graph_components.blocks import Block


class ArmBlock(Block):
    def __init__(
        self,
        name: str,
        config: dict[str, Any],
        path: str,
        block_type: str,
        attributes: dict[str, Any],
        id: str = "",
    ) -> None:
        super().__init__(name, config, path, block_type, attributes, id, GraphSource.ARM)

    def should_run_get_inner_attributes(self, attribute_value: Any) -> bool:
        """
        this function is triggered from _extract_inner_attributes to check whether we need to run the get_inner_attributes function.
        for ARM we want to get the inner_attributes also from list[str] and only for list[dict] like the rest of the frameworks,
        specific for the 'dependsOn' attribute in a resource
        """
        return isinstance(attribute_value, dict) or (isinstance(attribute_value, list) and len(attribute_value) > 0)
