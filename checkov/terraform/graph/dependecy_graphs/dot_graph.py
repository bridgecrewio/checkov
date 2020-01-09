from checkov.terraform.graph.dependency_graph import DependencyGraph
import subprocess
import tempfile
from networkx.drawing.nx_agraph import read_dot
import re
import dpath.util

TERRAFORM_RESERVED_WORDS = ['module', 'local', 'var', 'output', 'data', 'provider']
TERRAFORM_GRAPH_PREFIX = ["terraform", "graph"]
TERRAFORM_INIT_PREFIX = ["terraform", "init"]
DOT_REGEX = '\[root\] ([^ ]+)'
ASSIGNMENT_REGEX = '(output|var)\.([^ ]+)'
NON_PATH_WORDS_REGEX = '(output|var)\.'
DEFINITION_PATH_REGEX = '(([^ .]+)\.([^ .]+)(?!\.)?)'


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
    def _is_assignment_edge(e1, e2):
        return len(re.findall(ASSIGNMENT_REGEX, e2)) > 0

    def _init_terraform_directory(self):
        try:
            subprocess.call([*TERRAFORM_INIT_PREFIX, self.root_folder])
        except subprocess.CalledProcessError as e:
            self.logger.error(e.stderr)

    def _generate_dot_file(self):
        temp_dot_file = tempfile.NamedTemporaryFile(prefix="graph", suffix=".dot")
        try:
            subprocess.Popen([*TERRAFORM_GRAPH_PREFIX, self.root_folder], stdout=temp_dot_file).wait()
            self.dot_file = temp_dot_file
        except subprocess.CalledProcessError as e:
            self.logger.error(e.stderr)

    def _render_variables_assignments(self, tf_file, e1, e2):
        assignment_value = dpath.search(self.assignments[tf_file], e2, separator='.')
        if assignment_value and 'meta.count-boundary' not in e1:
            print(1)
            #TODO - continue handling of block types
            dpath.set(self.assignments[tf_file], e2, assignment_value)
        else:
            print(2)

    def compute_dependency_graph(self, root_folder):
        try:
            super()._populate_definitions_assignments()
            self._generate_dot_file()
            self.graph = read_dot(self.dot_file.name)
        finally:
            self.dot_file.close()

    def render_variables(self, tf_file):
        assignment_edges = [(self._parse_dot_to_definition(e1), self._parse_dot_to_definition(e2)) for (e1, e2, _) in
                            self.graph.edges if self._is_assignment_edge(e1, e2)]

        for (e1, e2) in assignment_edges:
            self._render_variables_assignments(tf_file, e1, e2)

        return self.tf_definitions
