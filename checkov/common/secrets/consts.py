from __future__ import annotations

from enum import Enum

GIT_HISTORY_NOT_BEEN_REMOVED = "not-removed"


class ValidationStatus(Enum):
    PRIVILEGED = "Privileged"
    VALID = "Valid"
    INVALID = "Invalid"
    UNKNOWN = "Unknown"
    UNAVAILABLE = "Unavailable"

    def __str__(self) -> str:
        # needed, because of a Python 3.11 change
        return self.value


SECRET_VALIDATION_STATUSES = {
    ValidationStatus.VALID.value,
    ValidationStatus.PRIVILEGED.value,
    ValidationStatus.INVALID.value,
    ValidationStatus.UNKNOWN.value,
    ValidationStatus.UNAVAILABLE.value,
}


class VerifySecretsResult(Enum):
    INSUFFICIENT_PARAMS = "INSUFFICIENT_PARAMS"
    FAILURE = "FAILURE"
    SUCCESS = "SUCESS"

    def __str__(self) -> str:
        # needed, because of a Python 3.11 change
        return self.value
