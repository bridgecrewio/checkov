class BaseGraphCheck:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.resource_types = []
        self.connected_resources_types = []
        self.operator = ''
        self.attribute = ''
        self.attribute_value = ''
        self.sub_checks = []
        self.type = None
        self.solver = None

    def set_solver(self, solver):
        self.solver = solver

    def run(self, graph_connector):
        return self.solver.run(graph_connector=graph_connector)
