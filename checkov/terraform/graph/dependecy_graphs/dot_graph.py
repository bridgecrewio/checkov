from checkov.terraform.graph.dependency_graph import DependencyGraph
import subprocess
import tempfile
from networkx.drawing.nx_agraph import read_dot
import re
import dpath.util
import collections

TERRAFORM_RESERVED_WORDS = ['module', 'local', 'var', 'output', 'data', 'provider']
TERRAFORM_GRAPH_PREFIX = ["terraform", "graph"]
TERRAFORM_INIT_PREFIX = ["terraform", "init"]
DOT_REGEX = '\[root\] ([^ ]+)'
ASSIGNMENT_REGEX = '(output|var|local)\.([^ ]+)'
NON_PATH_WORDS_REGEX = r'\b(?!output)[^ .]+'
TERRAFORM_TYPES_REGEX = r'(?=output|local|var|module|null_resource)[^ .]+'
DEFINITION_PATH_REGEX = '(([^ .]+)\.([^ .]+)(?!\.)?)'
MODULE_IN_PATH_REGEX = r'(module\.[^ .]+)\.'


def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class DotGraph(DependencyGraph):

    def __init__(self, root_folder, tf_definitions):
        graph_type = 'DOT'
        self.dot_file = None
        super().__init__(root_folder=root_folder, graph_type=graph_type, tf_definitions=tf_definitions)
        self._init_terraform_directory()

    @staticmethod
    def _parse_dot_to_definition(dot_label):
        return re.match(DOT_REGEX, dot_label).group(1)

    @staticmethod
    def _is_assignment_edge(e2):
        return len(re.findall(ASSIGNMENT_REGEX, e2)) > 0

    def _init_terraform_directory(self):
        try:
            subprocess.call([*TERRAFORM_INIT_PREFIX, self.root_folder])
        except subprocess.CalledProcessError as e:
            self.logger.error(e.stderr)

    @staticmethod
    def _wildcard_terraform_keywords(path):
        return re.sub(TERRAFORM_TYPES_REGEX, '*', path)

    @staticmethod
    def _strip_terraform_keywords(path):
        return ".".join(re.findall(NON_PATH_WORDS_REGEX, path))

    @staticmethod
    def _is_variable_found(var_regex, expression):
        if re.findall(var_regex, expression):
            return True
        return False

    def _generate_dot_file(self):
        temp_dot_file = tempfile.NamedTemporaryFile(prefix="graph", suffix=".dot")
        try:
            subprocess.Popen([*TERRAFORM_GRAPH_PREFIX, self.root_folder], stdout=temp_dot_file).wait()
            self.dot_file = temp_dot_file
        except subprocess.CalledProcessError as e:
            self.logger.error(e.stderr)

    def _fetch_assignment(self, tf_file, path):
        # First hierarchy search
        if dpath.search(self.assignments[tf_file], f'{path}', separator='.'):
            return {
                'assignment_path': path,
                'assignment': dpath.get(self.assignments[tf_file], f'{path}', separator='.'),
                'assignment_file': tf_file
            }
        wildcard_query = self._wildcard_terraform_keywords(path)
        # Second hierarchy search
        if dpath.search(self.assignments[tf_file], f'*.{wildcard_query}', separator='.'):
            return {
                'assignment_path': path,
                'assignment': dpath.get(self.assignments[tf_file], f'*.{wildcard_query}', separator='.'),
                'assignment_file': tf_file
            }
        if re.match(MODULE_IN_PATH_REGEX, path):
            module_subpath = re.match(MODULE_IN_PATH_REGEX, path).group(1)
            reduced_path = re.sub(MODULE_IN_PATH_REGEX, '', path, 1)
            # Module traversal if source available
            if dpath.search(self.assignments[tf_file], f'{module_subpath}.var.source', separator='.'):
                module_source_file = dpath.get(self.assignments[tf_file], f'{module_subpath}.var.source', separator='.')
                module_files = [file for file in self.assignments.keys() if module_source_file in file]

                for module_file in module_files:
                    return self._fetch_assignment(module_file, reduced_path)
        return {'assignment_file': tf_file}

    def _generate_assignment_regex(self, path):
        assignment_regex = self._strip_terraform_keywords(path)
        if 'var' in assignment_regex:
            # Look for level-file variable, without the module prefix (if exists)
            assignment_regex = re.findall(r'(var\.[^ .]+)', assignment_regex)[0]
        return r'(?:\$\{)?' + re.escape(assignment_regex) + r'\}?'

    def _is_assignment_exists(self, tf_file, e1, e2):
        if 'meta.count-boundary' in e1 or 'meta.count-boundary' in e2:
            return False
        if dpath.search(self.assignments[tf_file], f'**.{e2}', separator='.'):
            return True
        return False

    def _render_expression(self, render_regex, rendered_value, expression):
        if isinstance(rendered_value, dict):
            self.logger.warning(f'Rendering of dict values are not supported yet: {expression}')
            return None
        return re.sub(render_regex, str(rendered_value), expression)

    def _render_assignments_placeholders(self, tf_file, e1, e2):
        if self._is_assignment_exists(tf_file, e1, e2):
            edge_rendered_vars = {}
            assignment_key_fetch = self._fetch_assignment(tf_file, e1)
            assignment_value_fetch = self._fetch_assignment(tf_file, e2)

            assignment_object = assignment_key_fetch.get('assignment')
            assignment_key_file = assignment_key_fetch.get('assignment_file')
            assignment_value = assignment_value_fetch.get('assignment')

            render_assignment_regex = self._generate_assignment_regex(e2)

            if assignment_value is None or not assignment_object:
                self.logger.debug(f'assignment {e1} and/or {e2} could not be found')
                return
            assignment_key = self._wildcard_terraform_keywords(assignment_key_fetch.get('assignment_path'))
            if isinstance(assignment_object, list):
                expression = assignment_key_fetch[0]
                rendered_expression = self._render_expression(render_assignment_regex, assignment_value, expression)
                if rendered_expression:
                    dpath.new(edge_rendered_vars, assignment_key, rendered_expression)
            if isinstance(assignment_object, dict):
                for key, expression in flatten(assignment_object).items():
                    if self._is_variable_found(render_assignment_regex, str(expression)):
                        rendered_expression = self._render_expression(render_assignment_regex, assignment_value,
                                                                      expression)
                        if rendered_expression:
                            if dpath.search(self.assignments[assignment_key_file], f'*.{assignment_key}',
                                            separator='.'):
                                # It means it's a resource
                                assignment_key = self._wildcard_terraform_keywords(f'resource.{assignment_key}.{key}')
                            else:
                                assignment_key = self._wildcard_terraform_keywords(f'{assignment_key}.{key}')
                            dpath.new(edge_rendered_vars, assignment_key, rendered_expression)
            else:
                # It's a value
                expression = assignment_key_fetch.get('assignment')
                rendered_expression = self._render_expression(render_assignment_regex, assignment_value, expression)
                if rendered_expression:
                    dpath.new(edge_rendered_vars, assignment_key, rendered_expression)

            for key in edge_rendered_vars:
                dpath.set(self.assignments[assignment_key_file], f'{key}', edge_rendered_vars[key], separator='.')
                self.logger.debug(f'ASSIGNED: {key} -> {assignment_value} in file {assignment_key_file}')

    def compute_dependency_graph(self, root_folder):
        try:
            super()._populate_definitions_assignments()
            self._generate_dot_file()
            self.graph = read_dot(self.dot_file.name)
        finally:
            self.dot_file.close()

    def render_variables(self, tf_file):
        assignment_edges = [(self._parse_dot_to_definition(e1), self._parse_dot_to_definition(e2)) for (e1, e2, _) in
                            self.graph.edges if self._is_assignment_edge(e2)]

        for (e1, e2) in assignment_edges:
            self._render_assignments_placeholders(tf_file, e1, e2)

        return self.tf_definitions
