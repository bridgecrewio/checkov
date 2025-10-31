from typing import Optional, Any, Dict, Set, Tuple, Union, List
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

        # Convert the solver value into sets of IPv4 and IPv6 CIDR networks
        allowed_ranges_v4, allowed_ranges_v6 = self._to_cidr_sets(self.value)
        # Convert the vertex attribute to sets of IPv4 and IPv6 CIDR networks
        vertex_ranges_v4, vertex_ranges_v6 = self._to_cidr_sets(attr_val)

        # Check if all vertex ranges are subsets of at least one of the allowed ranges
        v4_subset_check = all(
            any(vertex_cidr.subnet_of(allowed_cidr) for allowed_cidr in allowed_ranges_v4)
            for vertex_cidr in vertex_ranges_v4
        )
        v6_subset_check = all(
            any(vertex_cidr.subnet_of(allowed_cidr) for allowed_cidr in allowed_ranges_v6)
            for vertex_cidr in vertex_ranges_v6
        )

        return v4_subset_check and v6_subset_check

    @staticmethod
    def _to_cidr_sets(value: Union[str, List[str], Set[str]]) -> Tuple[Set[ipaddress.IPv4Network], Set[ipaddress.IPv6Network]]:
        """
        Converts a value (string, list, set, etc.) into separate sets of IPv4Network and IPv6Network objects.
        """
        cidr_set_v4 = set()
        cidr_set_v6 = set()
        if isinstance(value, str):
            network = ipaddress.ip_network(value, strict=False)
            if isinstance(network, ipaddress.IPv4Network):
                cidr_set_v4.add(network)
            elif isinstance(network, ipaddress.IPv6Network):
                cidr_set_v6.add(network)
        elif isinstance(value, (list, set)):
            for v in value:
                network = ipaddress.ip_network(v, strict=False)
                if isinstance(network, ipaddress.IPv4Network):
                    cidr_set_v4.add(network)
                elif isinstance(network, ipaddress.IPv6Network):
                    cidr_set_v6.add(network)
        else:
            raise ValueError(f"Unsupported type for CIDR conversion: {type(value)}")
        return cidr_set_v4, cidr_set_v6
