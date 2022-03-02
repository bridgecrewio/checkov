from enum import Enum


class BlockType(str, Enum):
    DOCUMENT = "yamldocument"
    OBJECT = "yamlobject"
    ARRAY = "yamlarray"
    SCALAR = "yamlscalar"
