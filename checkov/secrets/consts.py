from enum import Enum


class ValidationStatus(Enum):
    PRIVILEGED = 'Privileged'
    VALID = 'Valid'
    INVALID = 'Invalid'
    UNKNOWN = 'Unknown'

    def __str__(self) -> str:
        # needed, because of a Python 3.11 change
        return self.value


class VerifySecretsResult(Enum):
    INSUFFICIENT_PARAMS = 'INSUFFICIENT_PARAMS'
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCESS'

    def __str__(self) -> str:
        # needed, because of a Python 3.11 change
        return self.value
