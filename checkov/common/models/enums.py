from enum import Enum


class CheckResult(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    # Unknown should be used when a check does not wish to return a result, generally due to the inability
    # to resolve a value or similar types of errors.
    UNKNOWN = "UNKNOWN"
    # Skipped is used by the framework when a test is suppressed and should not be used directly by checks.
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
    SUPPLY_CHAIN = 11
    API_SECURITY = 12


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
