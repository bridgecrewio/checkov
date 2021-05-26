class Edge:
    def __init__(self, origin: int, dest: int, label: str) -> None:
        self.origin = origin
        self.dest = dest
        self.label = label

    def __str__(self) -> str:
        return f"[{self.origin} -({self.label})-> {self.dest}]"
