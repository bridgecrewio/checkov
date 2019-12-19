from checkov.terraform.graph.dependency_graph import DependencyGraph
import subprocess
import tempfile
from networkx.drawing.nx_agraph import read_dot

TERRAFORM_GRAPH_PREFIX = ["terraform", "graph"]
TERRAFORM_INIT_PREFIX = ["terraform", "init"]


class DotGraph(DependencyGraph):

    def __init__(self, root_folder):
        graph_type = 'DOT'
        self.dot_file = None
        super().__init__(root_folder=root_folder, graph_type=graph_type)
        self._init_terraform_directory()

    def _init_terraform_directory(self):
        try:
            subprocess.call([*TERRAFORM_INIT_PREFIX, self.root_folder])
        except subprocess.CalledProcessError as e:
            self.logger.error(e.stderr)

    def _generate_dot_file(self):
        temp_dot_file = tempfile.NamedTemporaryFile(prefix="graph", suffix=".dot")
        try:
            subprocess.Popen([*TERRAFORM_GRAPH_PREFIX, self.root_folder],stdout=temp_dot_file).wait()
            self.dot_file = temp_dot_file
        except subprocess.CalledProcessError as e:
            self.logger.error(e.stderr)

    def compute_dependency_graph(self, root_folder):
        try:
            self._generate_dot_file()
            self.graph = read_dot(self.dot_file.name)
        finally:
            self.dot_file.close()

    def render_const_variables(self,tf_definitions):
        # TODO
        return tf_definitions
