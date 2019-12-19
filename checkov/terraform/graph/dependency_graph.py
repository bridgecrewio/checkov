import logging
from abc import ABC, abstractmethod

class DependencyGraph(ABC):

    def __init__(self, root_folder, graph_type):
        self.logger = logging.getLogger("{}".format(self.__module__))
        self.graph = None
        self.root_folder = root_folder
        self.graph_type = graph_type

    @abstractmethod
    def compute_dependency_graph(self, root_dir):
        raise NotImplementedError()

    @abstractmethod
    def render_const_variables(self):
        raise NotImplementedError()

