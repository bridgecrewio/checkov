from enum import Enum


class CheckResult(Enum):
    SUCCESS = 1
    FAILURE = 2
    UNKNOWN = 3


class CheckCategories(Enum):
    LOGGING = 1
    ENCRYPTION = 2
    GENERAL_SECURITY = 3
    NETWORKING = 4
    IAM = 5
    BACKUP_AND_RECOVERY = 6


class ContextCategories(Enum):
    PROVIDER = 1
    TERRAFORM = 2
    LOCALS = 3
    MODULE = 4
    DATA = 5
    RESOURCE = 6
    VARIABLE = 7
    OUTPUT = 8
