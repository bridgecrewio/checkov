from enum import Enum


class ValidationStatus(Enum):
    Privileged = 'Privileged'
    Valid = 'Valid'
    Invalid = 'Invalid'
    Unknown = 'Unknown'


class VerifySecretsResult(Enum):
    INSUFFICIENT_PARAMS = 'INSUFFICIENT_PARAMS'
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCESS'
