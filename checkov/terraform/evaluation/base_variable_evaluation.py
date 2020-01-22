from abc import ABC, abstractmethod
import logging


class BaseVariableEvaluation(ABC):
    def __init__(self, root_folder, tf_definitions, definitions_context):
        self.logger = logging.getLogger("{}".format(self.__module__))
        self.root_folder = root_folder
        self.tf_definitions = tf_definitions
        self.definitions_context = definitions_context

    @abstractmethod
    def evaluate_variables(self):
        raise NotImplementedError()
