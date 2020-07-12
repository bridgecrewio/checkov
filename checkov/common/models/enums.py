from enum import Enum


class CheckResult(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    SKIPPED = "SKIPPED"


class CheckCategories(Enum):
    LOGGING = 1
    ENCRYPTION = 2
    GENERAL_SECURITY = 3
    NETWORKING = 4
    IAM = 5
    BACKUP_AND_RECOVERY = 6
    CONVENTION = 7
    SECRETS = 8
    KUBERNETES = 9
    APPLICATION_SECURITY = 10


class OutputFormat(Enum):
    CONSOLE = 1
    JSON = 2
    JUNIT_XML = 3


class ContextCategories(Enum):
    PROVIDER = 1
    TERRAFORM = 2
    LOCALS = 3
    MODULE = 4
    DATA = 5
    RESOURCE = 6
    VARIABLE = 7
    OUTPUT = 8
