from dataclasses import dataclass


@dataclass
class BlockType:
    RESOURCE = "resource"

    def get(self, attr_name):
        return getattr(self, attr_name.upper())
