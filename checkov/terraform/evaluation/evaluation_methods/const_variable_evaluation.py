from checkov.terraform.evaluation.base_variable_evaluation import BaseVariableEvaluation
import os
import dpath
import re

NON_PATH_WORDS_REGEX = r'\b(?!output)[^ .]+'


class ConstVariableEvaluation(BaseVariableEvaluation):
    def __init__(self, tf_definitions, definitions_context):
        super().__init__(tf_definitions, definitions_context)

    @staticmethod
    def _strip_terraform_keywords(path):
        return ".".join(re.findall(NON_PATH_WORDS_REGEX, path))

    @staticmethod
    def _generate_var_evaluation_regex(path):
        return r'(?:\$\{)?var\.' + re.escape(path) + r'\}?'

    def _locate_assignments(self, folder, var_name):
        var_assignments_paths = {}
        assignment_regex = self._generate_var_evaluation_regex(var_name)
        for source_file in [file for file in os.listdir(folder) if file.endswith('.tf')]:
            file_path = os.path.join(folder, source_file)
            var_entries = dpath.search(self.tf_definitions[file_path], '**',
                                       afilter=lambda x: re.findall(assignment_regex, str(x)), yielded=True)
            var_assignments_paths[file_path] = []
            for definition_path, expression in var_entries:
                var_assignments_paths[file_path].append({'definition_expression': expression,
                                                         'definition_path': definition_path})
        var_assignments_paths = {k: v for (k, v) in var_assignments_paths.items() if len(v) > 0}
        return var_assignments_paths

    def _assign_definition_value(self, var_name, var_value, var_assignments_paths):
        assignment_regex = self._generate_var_evaluation_regex(var_name)
        for (assignment_file, assignments) in var_assignments_paths.items():
            # Save rendering information in context
            dpath.new(self.definitions_context[assignment_file], f'renders/{var_name}/value', var_value)
            dpath.new(self.definitions_context[assignment_file], f'renders/{var_name}/assignments', assignments)
            for assignment_obj in assignments:
                definition_path = assignment_obj.get('definition_path')
                entry_expression = assignment_obj.get('definition_expression')
                rendered_value = str(var_value)
                rendered_definition = re.sub(assignment_regex, rendered_value, entry_expression)
                dpath.set(self.tf_definitions[assignment_file], definition_path, rendered_definition)
                self.logger.debug(
                    f'Rendered default value of variable {var_name} in file {assignment_file} to {rendered_value}')

    def _render_folder_variables(self, folder):
        assignment_files = dpath.search(self.definitions_context, f'**.assignments', separator='.')
        variable_file_object = {k: v for k, v in assignment_files.items() if folder in k}
        if variable_file_object:
            for file_name, variable_assignments in variable_file_object.items():
                if variable_assignments.get('assignments'):
                    for var_name, var_value in variable_assignments['assignments'].items():
                        var_assignments_paths = self._locate_assignments(folder, var_name)
                        self._assign_definition_value(var_name, var_value, var_assignments_paths)

    # Render only variable which assignments are consts
    def evaluate_variables(self):
        definitions_folders = set([os.path.split(file_path)[0] for file_path in self.definitions_context.keys()])
        for folder in definitions_folders:
            self._render_folder_variables(folder)
