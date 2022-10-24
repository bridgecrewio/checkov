from enum import Enum


class BlockType(str, Enum):
    DOCUMENT = "jsondocument"
    OBJECT = "jsonobject"
    ARRAY = "jsonarray"
    SCALAR = "jsonscalar"
