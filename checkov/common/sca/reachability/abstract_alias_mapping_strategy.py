from abc import ABC, abstractmethod
from typing import List, Dict, Set


class AbstractAliasMappingStrategy(ABC):
    @abstractmethod
    def create_alias_mapping(self, repository_name: str, root_dir: str, relevant_packages: Set[str]) -> Dict[str, List[str]]:
        pass
