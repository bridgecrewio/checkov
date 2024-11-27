from typing import Optional, Any, Dict, Set
import ipaddress

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class CIDRRangeSubsetAttributeSolver(BaseAttributeSolver):
    operator = Operators.CIDR_RANGE_SUBSET  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        if attribute is None:
            return False  # Explicitly handle None attribute

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
        Filters out any IPv6 networks.
        """
        cidr_set = set()
        if isinstance(value, str):
            network = ipaddress.ip_network(value, strict=False)
            if isinstance(network, ipaddress.IPv4Network):
                cidr_set.add(network)
        elif isinstance(value, (list, set)):
            for v in value:
                network = ipaddress.ip_network(v, strict=False)
                if isinstance(network, ipaddress.IPv4Network):
                    cidr_set.add(network)
        else:
            raise ValueError(f"Unsupported type for CIDR conversion: {type(value)}")
        return cidr_set
