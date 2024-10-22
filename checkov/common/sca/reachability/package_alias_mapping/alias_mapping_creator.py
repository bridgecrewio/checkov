from __future__ import annotations

from typing import Dict, Set, Any

from checkov.common.sca.reachability.package_alias_mapping.abstract_alias_mapping_strategy import AbstractAliasMappingStrategy
from checkov.common.sca.reachability.package_alias_mapping.nodejs.nodejs_alias_mapping_strategy import NodejsAliasMappingStrategy

language_to_strategy: Dict[str, AbstractAliasMappingStrategy] = {
    "nodejs": NodejsAliasMappingStrategy()
}


class AliasMappingCreator:
    def __init__(self) -> None:
        self._alias_mapping: Dict[str, Any] = {"languages": {}}

    def update_alias_mapping_for_repository(
            self,
            repository_name: str,
            repository_root_dir: str,
            relevant_packages: Set[str]
    ) -> None:
        for lang in language_to_strategy:
            language_to_strategy[lang].update_alias_mapping(self._alias_mapping, repository_name, repository_root_dir, relevant_packages)

    def get_alias_mapping(self) -> Dict[str, Any]:
        return self._alias_mapping
