class Edge:
    def __init__(self, origin: int, dest: int, label: str) -> None:
        self.origin = origin
        self.dest = dest
        self.label = label

    def __str__(self) -> str:
        return f"[{self.origin} -({self.label})-> {self.dest}]"

    def __eq__(self, other) -> bool:
        return isinstance(other, Edge) and str(self) == str(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))