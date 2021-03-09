class Edge:
    def __init__(self, origin, dest, label):
        self.origin = origin
        self.dest = dest
        self.label = label

    def __str__(self):
        return f'[{self.origin} -({self.label})-> {self.dest}]'
