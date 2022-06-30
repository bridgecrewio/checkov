
class ExtraResource:
    __slots__ = ("file_abs_path", "file_path", "resource")

    def __init__(self, file_abs_path: str, file_path: str, resource: str):
        self.file_abs_path = file_abs_path
        self.file_path = file_path
        self.resource = resource  # resource ID
