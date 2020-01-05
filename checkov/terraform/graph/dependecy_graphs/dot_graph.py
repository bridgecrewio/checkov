from checkov.terraform.graph.dependency_graph import DependencyGraph
import subprocess
import tempfile
from networkx.drawing.nx_agraph import read_dot
import re

TERRAFORM_GRAPH_PREFIX = ["terraform", "graph"]
TERRAFORM_INIT_PREFIX = ["terraform", "init"]
DOT_REGEX = "\[root\] ([^ ]+)"


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
    def _is_var_edge(e1, e2):
        return 'var' in e2

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

    def _render_variables_assignments(self, e1, e2):
        pass

    def compute_dependency_graph(self, root_folder):
        try:
            self._generate_dot_file()
            self.graph = read_dot(self.dot_file.name)
        finally:
            self.dot_file.close()

    def render_variables(self):
        super()._populate_assignments_types(self.tf_definitions)
        var_edges = [(self._parse_dot_to_definition(e1), self._parse_dot_to_definition(e2)) for (e1, e2, _) in
                     self.graph.edges if self._is_var_edge(e1, e2)]

        for (e1, e2) in var_edges:
            self._render_variables_assignments(e1, e2)

        return self.tf_definitions
