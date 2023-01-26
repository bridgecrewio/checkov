from typing import Dict, Any

from checkov.common.policies3d.checks_infra.base_check import Base3dPolicyCheck


class Base3dPolicyCheckParser:
    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> Base3dPolicyCheck:
        raise NotImplementedError
