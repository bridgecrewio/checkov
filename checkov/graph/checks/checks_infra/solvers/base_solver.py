from abc import abstractmethod


class BaseSolver:
    operator = ''

    def __init__(self, query_type):
        self.query_type = query_type

    @abstractmethod
    def get_operation(self, *args):
        raise NotImplementedError()

    @abstractmethod
    def _get_operation(self, *args):
        raise NotImplementedError()

    @abstractmethod
    def run_query(self, graph_connector):
        raise NotImplementedError()

