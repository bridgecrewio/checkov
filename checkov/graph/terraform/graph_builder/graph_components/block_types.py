from enum import Enum


class BlockType(str, Enum):
    DATA = "data"
    LOCALS = "locals"
    MODULE = "module"
    OUTPUT = "output"
    PROVIDER = "provider"
    RESOURCE = "resource"
    TERRAFORM = "terraform"
    TF_VARIABLE = "tfvar"
    VARIABLE = "variable"
    CUSTOM = "custom"
