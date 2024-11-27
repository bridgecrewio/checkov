from typing import Optional, Any, Dict, Set, Union, List
import ipaddress

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class CIDRRangeSubsetAttributeSolver(BaseAttributeSolver):
    operator = Operators.CIDR_RANGE_SUBSET

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr_val = vertex.get(attribute)
        if not attr_val:
            return False

        # Convert the solver value into a set of CIDR networks
        allowed_ranges = self._to_cidr_set(self.value)
        # Convert the vertex attribute to a set of CIDR networks
        vertex_ranges = self._to_cidr_set(attr_val)

        # Check if all vertex ranges are subsets of at least one of the allowed ranges
        return all(any(vertex_cidr.subnet_of(allowed_cidr) for allowed_cidr in allowed_ranges) for vertex_cidr in
                   vertex_ranges)

    @staticmethod
    def _to_cidr_set(value: Any) -> Set[ipaddress.IPv4Network]:
        """
        Converts a value (string, list, set, etc.) into a set of IPv4Network objects.
        """
        if isinstance(value, str):
            return {ipaddress.ip_network(value, strict=False)}
        elif isinstance(value, (list, set)):
            return {ipaddress.ip_network(v, strict=False) for v in value}
        else:
            raise ValueError(f"Unsupported type for CIDR conversion: {type(value)}")
