import logging
import os
import re

import dpath

from checkov.terraform.evaluation.base_variable_evaluation import BaseVariableEvaluation


class ConstVariableEvaluation(BaseVariableEvaluation):
    def __init__(self, root_folder, tf_definitions, definitions_context):
        super().__init__(root_folder, tf_definitions, definitions_context)

    def _locate_variables_assignments(self, definition_type, folder, var_name):
        var_assignments_paths = {}
        assignment_regex = self._generate_evaluation_regex(definition_type, var_name)
        for source_file in [file for file in os.listdir(folder) if
                            file.endswith('.tf') and self.tf_definitions.get(os.path.join(folder, file))]:
            file_path = os.path.join(folder, source_file)
            var_entries = dpath.search(self.tf_definitions[file_path], '**',
                                       afilter=lambda x: re.findall(assignment_regex, str(x)), yielded=True)
            var_assignments_paths[file_path] = []
            for definition_path, expression in var_entries:
                context_path, definition_name = self.extract_context_path(definition_path)
                var_assignments_paths[file_path].append({
                    'definition_name': definition_name,
                    'definition_expression': expression,
                    'definition_path': definition_path})
        var_assignments_paths = {k: v for (k, v) in var_assignments_paths.items() if len(v) > 0}
        return var_assignments_paths

    def _assign_definition_value(self, definition_type, var_name, var_value, var_assignments):
        """
        assigns var_value to variable var_name in tf_definitions
        :param definition_type: the entity's block type
        :param var_name: variable name
        :param var_value: variable value
        :param var_assignments: variable assignments
        """
        assignment_regex = self._generate_evaluation_regex(definition_type, var_name)
        var_file = var_assignments['var_file']
        var_value_string = str(var_value)
        for (assignment_file, assignments) in var_assignments['definitions'].items():
            # Save evaluation information in context
            for assignment_obj in assignments:
                definition_path = assignment_obj.get('definition_path')
                entry_expression = assignment_obj.get('definition_expression')
                definition_name = assignment_obj.get('definition_name')
                if not isinstance(entry_expression, str):
                    # Example of unsupported evaluation:
                    # cidr_blocks = local.ip_ranges.ipv4Prefixes[*].prefix
                    logging.info(f'Ran into a complex evaluation which isn\'t supported yet, on {assignment_file}')
                    continue
                context_path, _ = self.extract_context_path(definition_path)
                if assignment_file in self.definitions_context.keys():
                    dpath.new(self.definitions_context[assignment_file], f'evaluations/{var_name}/var_file',
                              var_file)
                    dpath.new(self.definitions_context[assignment_file], f'evaluations/{var_name}/value',
                              var_value)
                    dpath.new(self.definitions_context[assignment_file],
                              f'evaluations/{var_name}/definitions',
                              assignments)
                if self._is_variable_only_expression(assignment_regex, entry_expression):
                    # Preserve the original type of the variable if not part of a composite expression
                    evaluated_definition = var_value
                else:
                    evaluated_definition = re.sub(assignment_regex, re.escape(var_value_string), entry_expression)

                dpath.set(self.tf_definitions[assignment_file], definition_path, evaluated_definition)
                self.logger.debug(
                    f'Evaluated definition {definition_name} in file {assignment_file}: default value of variable {var_file}: '
                    f'{var_name} to "{var_value_string}"')

    def evaluate_variables(self):
        """
        Evaluate all default variables found in tf_definitions expressions, per a scanned directory of Terraform files
        """
        definitions_folders = set([os.path.split(file_path)[0] for file_path in self.definitions_context.keys()])
        for folder in definitions_folders:
            self._evaluate_folder_variables(folder)

    def _evaluate_folder_variables(self, folder):
        """
        Locate all assignments extracted by the context parser, and assigns them to corresponding variables found in
        tf_definitions
        :param folder: folder to assign variables in
        :return:
        """
        assignment_files = dpath.search(self.definitions_context, f'**.assignments', separator='.')
        assignment_files = {k: v for k, v in assignment_files.items() if folder in k}
        if assignment_files:
            self._assign_definitions(assignment_files, folder)

    def _assign_definitions(self, assignment_files, folder):
        """
        assign variables in expressions under a Terraform folder
        :param assignment_files:
        :param folder:
        :return:
        """
        for var_file, variable_assignments in assignment_files.items():
            relative_var_file = f'/{os.path.relpath(var_file, self.root_folder)}'
            for definition_type in variable_assignments.keys():
                for var_name, var_value in variable_assignments[definition_type]['assignments'].items():
                    evaluated_definitions = self._locate_variables_assignments(definition_type, folder, var_name)
                    var_assignments = {'definitions': evaluated_definitions, 'var_file': relative_var_file}
                    self._assign_definition_value(definition_type, var_name, var_value, var_assignments)
