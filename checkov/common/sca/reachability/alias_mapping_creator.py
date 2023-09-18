from __future__ import annotations

from typing import Dict, Set, Any

from checkov.common.sca.reachability.abstract_alias_mapping_strategy import AbstractAliasMappingStrategy
from checkov.common.sca.reachability.nodejs.nodejs_alias_mapping_strategy import NodejsAliasMappingStrategy

language_to_strategy: Dict[str, AbstractAliasMappingStrategy] = {
    "nodejs": NodejsAliasMappingStrategy()
}


class AliasMappingCreator:
    def __init__(self, repository_name: str):
        self._repository_name = repository_name
        self._alias_mapping: Dict[str, Any] = {}

    def update_alias_mapping_for_repository(
            self,
            repository_name: str,
            repository_root_dir: str,
            relevant_packages: Set[str]
    ) -> None:
        pass