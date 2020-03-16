from checkov.terraform.evaluation.base_variable_evaluation import BaseVariableEvaluation
import os
import dpath
import re

NON_PATH_WORDS_REGEX = r'\b(?!output)[^ .]+'
TF_DEFINITIONS_STRIP_WORDS = r'\b(?!\d)([^\/]+)'


class ConstVariableEvaluation(BaseVariableEvaluation):
    def __init__(self, root_folder, tf_definitions, definitions_context):
        super().__init__(root_folder, tf_definitions, definitions_context)

    @staticmethod
    def _strip_terraform_keywords(path):
        return ".".join(re.findall(NON_PATH_WORDS_REGEX, path))

    @staticmethod
    def _generate_var_evaluation_regex(var_name):
        return r'((?:\$\{)?var\.' + re.escape(var_name) + r'(?:\})?)'

    @staticmethod
    def _extract_context_path(definition_path):
        return os.path.split("/".join(re.findall(TF_DEFINITIONS_STRIP_WORDS, definition_path)))

    @staticmethod
    def _is_variable_only_expression(assignment_regex, entry_expression):
        exact_assignment_regex = r'^' + assignment_regex + r'$'
        return len(re.findall(exact_assignment_regex, entry_expression)) > 0

    def _locate_assignments(self, folder, var_name):
        var_assignments_paths = {}
        assignment_regex = self._generate_var_evaluation_regex(var_name)
        for source_file in [file for file in os.listdir(folder) if
                            file.endswith('.tf') and self.tf_definitions.get(os.path.join(folder, file))]:
            file_path = os.path.join(folder, source_file)
            var_entries = dpath.search(self.tf_definitions[file_path], '**',
                                       afilter=lambda x: re.findall(assignment_regex, str(x)), yielded=True)
            var_assignments_paths[file_path] = []
            for definition_path, expression in var_entries:
                context_path, definition_name = self._extract_context_path(definition_path)
                var_assignments_paths[file_path].append({
                    'definition_name': definition_name,
                    'definition_expression': expression,
                    'definition_path': definition_path})
        var_assignments_paths = {k: v for (k, v) in var_assignments_paths.items() if len(v) > 0}
        return var_assignments_paths

    def _assign_definition_value(self, var_name, var_value, var_assignments):
        assignment_regex = self._generate_var_evaluation_regex(var_name)
        var_file = var_assignments['var_file']
        var_value_string = str(var_value)
        for (assignment_file, assignments) in var_assignments['definitions'].items():
            # Save evaluation information in context
            for assignment_obj in assignments:
                definition_path = assignment_obj.get('definition_path')
                entry_expression = assignment_obj.get('definition_expression')
                definition_name = assignment_obj.get('definition_name')
                context_path, _ = self._extract_context_path(definition_path)
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
                    evaluated_definition = re.sub(assignment_regex, var_value_string, entry_expression)

                dpath.set(self.tf_definitions[assignment_file], definition_path, evaluated_definition)
                self.logger.debug(
                    f'Evaluated definition {definition_name} in file {assignment_file}: default value of variable {var_file}: '
                    f'{var_name} to "{var_value_string}"')

    def _evaluate_folder_variables(self, folder):
        assignment_files = dpath.search(self.definitions_context, f'**.assignments', separator='.')
        variable_file_object = {k: v for k, v in assignment_files.items() if folder in k}
        if variable_file_object:
            for var_file, variable_assignments in variable_file_object.items():
                relative_var_file = f'/{os.path.relpath(var_file, self.root_folder)}'
                for var_name, var_value in variable_assignments['variable']['assignments'].items():
                    evaluated_definitions = self._locate_assignments(folder, var_name)
                    var_assignments = {'definitions': evaluated_definitions, 'var_file': relative_var_file}
                    self._assign_definition_value(var_name, var_value, var_assignments)

    # Evaluate only variable which assignments are consts
    def evaluate_variables(self):
        definitions_folders = set([os.path.split(file_path)[0] for file_path in self.definitions_context.keys()])
        for folder in definitions_folders:
            self._evaluate_folder_variables(folder)
