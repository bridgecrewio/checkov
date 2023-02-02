
from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class SastLanguages(ExtendedEnum):
    PYTHON = 'python'
    JAVA = 'java'
    JAVASCRIPT = 'javascript'
