from __future__ import annotations
from enum import Enum
from typing import Union


class ValidationStatus(Enum):
    PRIVILEGED = 'Privileged'
    VALID = 'Valid'
    INVALID = 'Invalid'
    UNKNOWN = 'Unknown'
    UNAVAILABLE = 'Unavailable'

    def __str__(self) -> str:
        # needed, because of a Python 3.11 change
        return self.value


SECRET_VALIDATION_STATUSES = [ValidationStatus.VALID.value,
                              ValidationStatus.PRIVILEGED.value,
                              ValidationStatus.INVALID.value,
                              ValidationStatus.UNKNOWN.value,
                              ValidationStatus.UNAVAILABLE.value]


class VerifySecretsResult(Enum):
    INSUFFICIENT_PARAMS = 'INSUFFICIENT_PARAMS'
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCESS'

    def __str__(self) -> str:
        # needed, because of a Python 3.11 change
        return self.value


GIT_HISTORY_NOT_BEEN_REMOVED = 'not-removed'
ADDED = 'added'
REMOVED = 'removed'
GIT_HISTORY_OPTIONS = {ADDED, REMOVED}


Commit = dict[str, Union[str, dict[str, str], list[str]]]
COMMIT_HASH_KEY = '==commit_hash=='
COMMIT_COMMITTER = '==committer=='
COMMIT_DATETIME = '==committed_datetime=='
COMMIT_CONSTANTS = {COMMIT_HASH_KEY, COMMIT_COMMITTER, COMMIT_DATETIME}


