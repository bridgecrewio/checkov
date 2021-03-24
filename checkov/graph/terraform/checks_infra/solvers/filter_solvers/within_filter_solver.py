from checkov.graph.terraform.checks_infra.solvers.filter_solvers.base_filter_solver import BaseFilterSolver
from checkov.graph.terraform.utils.utils import decode_graph_property_value, encode_graph_property_value


class WithinFilterSolver(BaseFilterSolver):
    operator = 'within'

    def __init__(self, resource_types, query_attribute, query_value):
        query_value = decode_graph_property_value(query_value)
        query_value = [encode_graph_property_value(val) for val in query_value]
        super().__init__(resource_types=resource_types,
                         query_attribute=query_attribute, query_value=query_value)

    def get_operation(self, **kwargs):
        # TODO
        raise NotImplementedError
