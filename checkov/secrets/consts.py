from __future__ import annotations
from enum import Enum
from typing import Union, TypedDict, Final


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


class CommitMetadata(TypedDict, total=False):
    __commit_hash_key__: str
    __committer__: str
    __committed_datetime__: str


COMMIT_METADATA: Final = "__commit_metadata__"
COMMIT_HASH_KEY: Final = "__commit_hash_key__"
COMMIT_COMMITTER: Final = '__committer__'
COMMIT_DATETIME: Final = '__committed_datetime__'
COMMIT_CONSTANTS = {COMMIT_HASH_KEY, COMMIT_COMMITTER, COMMIT_DATETIME}

Commit = dict[str, Union[str, CommitMetadata]]
