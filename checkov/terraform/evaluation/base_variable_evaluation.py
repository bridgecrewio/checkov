from abc import ABC, abstractmethod
import logging
import os
import re
import dpath.util

TF_DEFINITIONS_STRIP_WORDS = r'\b(?!\d)([^\/]+)'


class BaseVariableEvaluation(ABC):
    def __init__(self, root_folder, tf_definitions, definitions_context):
        self.logger = logging.getLogger("{}".format(self.__module__))
        self.root_folder = root_folder
        self.tf_definitions = tf_definitions
        self.definitions_context = definitions_context

    @abstractmethod
    def evaluate_variables(self):
        raise NotImplementedError()

    @staticmethod
    # Converts a JSONPath (dpath standard) definition entry path into valid context parser path
    def extract_context_path(definition_path):
        return os.path.split("/".join(re.findall(TF_DEFINITIONS_STRIP_WORDS, definition_path)))

    @staticmethod
    def reduce_entity_evaluations(variables_evaluations, entity_context_path):
        entity_evaluations = {}
        for var_name, variable_evaluations in variables_evaluations.items():
            entity_definitions = []
            for var_definition in variable_evaluations['definitions']:
                var_context_path, _ = BaseVariableEvaluation.extract_context_path(var_definition['definition_path'])
                variable_context_path = var_context_path.split("/")
                # This is due to inconsistency in order of Terraform entity naming conventions
                if set(variable_context_path) == set(entity_context_path):
                    entity_definitions.append(var_definition)
            if entity_definitions:
                entity_evaluation = variables_evaluations[var_name]
                entity_evaluation['definitions'] = entity_definitions
                dpath.new(entity_evaluations, var_name, entity_evaluation)
        return entity_evaluations
