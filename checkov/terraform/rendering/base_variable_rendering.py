from abc import ABC, abstractmethod
import logging


class BaseVariableRendering(ABC):
    def __init__(self, tf_definitions, definitions_context):
        self.logger = logging.getLogger("{}".format(self.__module__))
        self.tf_definitions = tf_definitions
        self.definitions_context = definitions_context

    @abstractmethod
    def render_variables(self):
        raise NotImplementedError()
