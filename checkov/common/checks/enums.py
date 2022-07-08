from enum import Enum


class BlockType(str, Enum):
    DOCUMENT = "document"
    OBJECT = "object"
    ARRAY = "array"
    SCALAR = "scalar"
