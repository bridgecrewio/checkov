from abc import ABC, abstractmethod
from typing import List, Dict, Set


class AliasMappingStrategy(ABC):
    @abstractmethod
    def create_alias_mapping(self, root_dir: str, relevant_packages: Set[str]) -> Dict[str, List[str]]:
        pass
