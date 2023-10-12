from __future__ import annotations

import logging
from typing import Optional, TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from detect_secrets.core.potential_secret import PotentialSecret

PROHIBITED_FILES = ('Pipfile.lock', 'yarn.lock', 'package-lock.json', 'requirements.txt', 'go.sum')


ADDED = 'added'
REMOVED = 'removed'
GIT_HISTORY_OPTIONS = {ADDED, REMOVED}


CommitDiff = str


class RenamedFile(TypedDict):
    rename_from: str
    rename_to: str


class Commit:
    __slots__ = ("metadata", "files", "renamed_files")

    def __init__(
            self,
            metadata: CommitMetadata,
            files: dict[str, CommitDiff] | None = None,
            renamed_files: dict[str, RenamedFile] | None = None
    ):
        self.metadata: CommitMetadata = metadata
        self.files: dict[str, CommitDiff] = files or {}
        self.renamed_files: dict[str, RenamedFile] = renamed_files or {}

    def is_empty(self) -> bool:
        return not bool(self.files or self.renamed_files)

    def add_file(self, filename: str, commit_diff: CommitDiff) -> None:
        if self.files.get(filename):
            logging.warning(f'add_file-file {filename} already exist in commit')
            return
        self.files[filename] = commit_diff

    def rename_file(self, file_path: str, prev_filename: str, new_filename: str) -> None:
        if self.renamed_files.get(new_filename):
            logging.warning(f"rename_file-new filename {new_filename} was already renamed, might be an error")
            return
        self.renamed_files[file_path] = {
            'rename_from': prev_filename,
            'rename_to': new_filename
        }

    def remove_file(self, filename: str) -> None:
        if self.files.get(filename):
            del self.files[filename]


class CommitMetadata:
    __slots__ = ("commit_hash", "committer", "committed_datetime")

    def __init__(self, commit_hash: str, committer: str, committed_datetime: str):
        self.commit_hash: str = commit_hash
        self.committer: str = committer
        self.committed_datetime: str = committed_datetime


class EnrichedPotentialSecretMetadata(TypedDict, total=False):
    added_commit_hash: str
    removed_commit_hash: str
    code_line: Optional[str]
    added_by: Optional[str]
    removed_date: Optional[str]
    added_date: Optional[str]


class EnrichedPotentialSecret(EnrichedPotentialSecretMetadata):
    potential_secret: PotentialSecret  # noqa: CCE003  # a static attribute
