from abc import ABC, abstractmethod
import logging
import os
import re
from typing import Tuple, Dict, Any, List

import dpath

from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger

TF_DEFINITIONS_STRIP_WORDS = re.compile(r"\b(?!\d)([^\/]+)")
NON_PATH_WORDS_REGEX = re.compile(r"\b(?!output)[^ .]+")
DEFINITION_TYPES_REGEX_MAPPING = {"variable": "var", "locals": "local"}


class BaseVariableEvaluation(ABC):
    def __init__(
        self,
        root_folder: str,
        tf_definitions: Dict[str, Dict[str, Any]],
        definitions_context: Dict[str, Dict[str, Any]],
    ) -> None:
        self.logger = logging.getLogger("{}".format(self.__module__))
        add_resource_code_filter_to_logger(self.logger)
        self.root_folder = root_folder
        self.tf_definitions = tf_definitions
        self.definitions_context = definitions_context

    @abstractmethod
    def evaluate_variables(self) -> Any:
        """
        evaluate variables of tf_definitions entities
        :return:
        """
        raise NotImplementedError()

    @staticmethod
    def extract_context_path(definition_path: str) -> Tuple[str, str]:
        """
        Converts a JSONPath (dpath library standard) definition entry path into valid context parser path
        :param definition_path: entity's JSONPath syntax path in tf_definitions
        :return:entity path in context parser
        """
        return os.path.split("/".join(re.findall(TF_DEFINITIONS_STRIP_WORDS, definition_path)))

    @staticmethod
    def reduce_entity_evaluations(
        variables_evaluations: Dict[str, Dict[str, Any]], entity_context_path: List[str]
    ) -> Dict[str, Any]:
        """
        Reduce variable evaluations only to variables that are included in the entity's code block
        :param variables_evaluations:
        :param entity_context_path:
        :return: the variable evaluations of the entity
        """
        entity_evaluations: Dict[str, Any] = {}
        for var_name, variable_evaluations in variables_evaluations.items():
            entity_definitions = []
            for var_definition in variable_evaluations["definitions"]:
                var_context_path, _ = BaseVariableEvaluation.extract_context_path(var_definition["definition_path"])
                variable_context_path = var_context_path.split("/")
                # This is due to inconsistency in order of Terraform entity naming conventions
                if set(variable_context_path) == set(entity_context_path):
                    entity_definitions.append(var_definition)
            if entity_definitions:
                entity_evaluation = variables_evaluations[var_name]
                entity_evaluation["definitions"] = entity_definitions
                dpath.new(entity_evaluations, var_name, entity_evaluation)
        return entity_evaluations
