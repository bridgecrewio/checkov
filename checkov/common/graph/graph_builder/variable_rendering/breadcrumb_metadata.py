class BreadcrumbMetadata:
    __slots__ = ("attribute_key", "vertex_id")

    def __init__(self, vertex_id: int, attribute_key: str):
        self.vertex_id = vertex_id
        self.attribute_key = attribute_key
