from enum import Enum


class ValidationStatus(Enum):
    PRIVILEGED = 'Privileged'
    VALID = 'Valid'
    INVALID = 'Invalid'
    UNKNOWN = 'Unknown'


class VerifySecretsResult(Enum):
    INSUFFICIENT_PARAMS = 'INSUFFICIENT_PARAMS'
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCESS'
