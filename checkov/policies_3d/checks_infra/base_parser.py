from abc import abstractmethod
from typing import Dict, Any

from checkov.policies_3d.checks_infra.base_check import Base3dPolicyCheck


class Base3dPolicyCheckParser:
    @abstractmethod
    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> Base3dPolicyCheck:
        pass
