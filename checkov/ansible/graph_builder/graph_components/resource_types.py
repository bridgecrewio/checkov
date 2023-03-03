from enum import Enum


class ResourceType(str, Enum):
    BLOCK = "block"
    TASKS = "tasks"

    def __str__(self) -> str:
        # needed, because of a Python 3.11 change
        return self.value
