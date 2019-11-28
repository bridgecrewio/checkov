from enum import Enum


class ScanResult(Enum):
    SUCCESS = 1
    FAILURE = 2
    UNKNOWN = 3


class ScanCategories(Enum):
    LOGGING = 1
    ENCRYPTION = 2
    GENERAL_SECURITY = 3
    NETWORKING = 4
    IAM = 5
    BACKUP_AND_RECOVERY = 6
