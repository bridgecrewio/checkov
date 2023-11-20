from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, TypedDict

from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.secrets import omit_secret_value_from_line
from checkov.common.secrets.consts import GIT_HISTORY_NOT_BEEN_REMOVED
from checkov.secrets.git_types import EnrichedPotentialSecretMetadata, EnrichedPotentialSecret, Commit, ADDED, REMOVED, \
    GIT_HISTORY_OPTIONS, CommitDiff

if TYPE_CHECKING:
    from detect_secrets.core.potential_secret import PotentialSecret

RENAME_STR = 'rename'
FILE_RESULTS_STR = 'file_results'
RAW_STORE_TYPES = {RENAME_STR, FILE_RESULTS_STR}


class RawStore(TypedDict):
    file_results: List[PotentialSecret]
    file_name: str
    commit: Commit
    type: str  # rename / file results
    rename_from: str
    rename_to: str


class GitHistorySecretStore:
    def __init__(self) -> None:
        self.secrets_by_file_value_type: Dict[str, List[EnrichedPotentialSecret]] = {}

    def set_secret_map(self, file_results: List[PotentialSecret], file_name: str, commit: Commit) -> None:
        # First find if secret was moved in the file
        equal_secret_in_commit: Dict[str, List[str]] = defaultdict(list)
        for secret in file_results:
            secret_key = get_secret_key(file_name, secret.secret_hash, secret.type)
            equal_secret_in_commit[secret_key].append(ADDED if secret.is_added else REMOVED)

        for secret in file_results:
            if not secret.filename or 'None' in secret.filename:
                secret.filename = file_name
            secret_key = get_secret_key(file_name, secret.secret_hash, secret.type)
            if all(value in equal_secret_in_commit[secret_key] for value in GIT_HISTORY_OPTIONS):
                continue
            if secret.is_added:
                self._add_new_secret(secret_key, secret, commit)
            if secret.is_removed:
                self._update_removed_secret(secret_key, secret, file_name, commit)

    def _add_new_secret(self, secret_key: str, secret: PotentialSecret, commit: Commit) -> None:
        if secret_key not in self.secrets_by_file_value_type:
            self.secrets_by_file_value_type[secret_key] = []
        else:
            all_removed = all(
                potential_secret.get('removed_commit_hash') for potential_secret in
                self.secrets_by_file_value_type[secret_key])
            # Update secret map with the new potential secret
            if all_removed:
                self.secrets_by_file_value_type[secret_key][0].update({'potential_secret': secret,
                                                                       'removed_commit_hash': '',
                                                                       'removed_date': ''})
                return
        code_line = search_for_code_line(commit.files[secret.filename], secret.secret_value, secret.is_added)
        enriched_potential_secret: EnrichedPotentialSecret = {
            'added_commit_hash': commit.metadata.commit_hash,
            'removed_commit_hash': '',
            'potential_secret': secret,
            'code_line': code_line,
            'added_by': commit.metadata.committer,
            'removed_date': '',
            'added_date': commit.metadata.committed_datetime
        }
        self.secrets_by_file_value_type[secret_key].append(enriched_potential_secret)

    def _update_removed_secret(self, secret_key: str, secret: PotentialSecret, file_name: str, commit: Commit) -> None:
        # Try to find the corresponding added secret in the git history secret map
        secrets_in_file = self.secrets_by_file_value_type.get(secret_key, None)
        if secrets_in_file:
            for secret_in_file in secrets_in_file:
                if secret_in_file['potential_secret'].is_added:
                    secret_in_file['removed_commit_hash'] = commit.metadata.commit_hash
                    secret_in_file['potential_secret'] = secret
                    secret_in_file['removed_date'] = commit.metadata.committed_datetime
                    break
        else:
            logging.warning(f"No added secret commit found for secret in file {file_name}.")

    def handle_renamed_file(self, rename_from: str, rename_to: str, commit: Commit) -> None:
        temp_secrets_by_file_value_type: Dict[str, List[EnrichedPotentialSecret]] = {}
        for secret_key in self.secrets_by_file_value_type.keys():
            if rename_from in secret_key:
                new_secret_key = secret_key.replace(rename_from, rename_to)
                temp_secrets_by_file_value_type[new_secret_key] = []
                secret_in_file = self.secrets_by_file_value_type[secret_key]
                for secret_data in secret_in_file:
                    # defines the secret in the old file as removed and add the secret to the new file
                    secret_data['removed_commit_hash'] = commit.metadata.commit_hash
                    secret_data['removed_date'] = commit.metadata.committed_datetime
                    new_secret = pickle_deepcopy(secret_data['potential_secret'])
                    new_secret.filename = rename_to
                    code = secret_data.get('code_line')
                    enriched_potential_secret: EnrichedPotentialSecret = {
                        'added_commit_hash': commit.metadata.commit_hash,
                        'removed_commit_hash': '',
                        'potential_secret': new_secret,
                        'code_line': code,
                        'added_by': secret_data.get('added_by'),
                        'removed_date': '',
                        'added_date': secret_data.get('added_date')
                    }
                    temp_secrets_by_file_value_type[new_secret_key].append(enriched_potential_secret)
        self.secrets_by_file_value_type.update(temp_secrets_by_file_value_type)

    def get_added_and_removed_commit_hash(self, key: str, secret: PotentialSecret, root_folder: Optional[str]) -> EnrichedPotentialSecretMetadata:
        """
        now we have only the current commit_hash - in the added_commit_hash or in the removed_commit_hash.
        in the next step we will add the connection and the missing data
        The key is built like this:
        '{added_commit_hash}_{removed_commit_hash or the string GIT_HISTORY_NOT_BEEN_REMOVED
        if the secret not been removed}_{file_name}'
        returns (added, removed, code)
        """
        try:
            secret_key = get_secret_key(secret.filename, secret.secret_hash, secret.type)  # by value type
            enriched_secrets: List[EnrichedPotentialSecret] = self.secrets_by_file_value_type.get(secret_key, [])
            if not enriched_secrets and root_folder:
                # sometimes the secret key is from the project path instead of abs path
                filename = f'{root_folder}/{secret.filename}'
                secret_key = get_secret_key(filename, secret.secret_hash, secret.type)  # by value type
                enriched_secrets = self.secrets_by_file_value_type.get(secret_key, [])
                if not enriched_secrets:
                    logging.warning(f'Did not find added_commit_hash and removed_commit_hash for {secret_key}')
                    return {}
            chosen_secret = enriched_secrets[0]
            if len(enriched_secrets) > 1:
                res = key.split("_")
                added, removed = res[0], res[1]
                if removed == GIT_HISTORY_NOT_BEEN_REMOVED:
                    removed = ''
                for enriched_secret in enriched_secrets:
                    if added == enriched_secret.get('added_commit_hash') and \
                            removed == enriched_secret.get('removed_commit_hash'):
                        chosen_secret = enriched_secret
                        break

            return {
                'added_commit_hash': chosen_secret.get('added_commit_hash', ''),
                'removed_commit_hash': chosen_secret.get('removed_commit_hash', ''),
                'code_line': chosen_secret.get('code_line'),
                'added_by': chosen_secret.get('added_by'),
                'removed_date': chosen_secret.get('removed_date'),
                'added_date': chosen_secret.get('added_date')
            }
        except Exception as e:
            logging.warning(f"Failed set added_commit_hash and removed_commit_hash due to: {str(e)}")
            return {}


def search_for_code_line(commit_diff: CommitDiff, secret_value: Optional[str], is_added: Optional[bool]) -> str:
    if not commit_diff:
        logging.warning(f'missing file name for {commit_diff}, hence no available code line')
    if secret_value is None:
        return ''
    splitted = commit_diff.split('\n')
    start_char = '+' if is_added else '-'
    for line in splitted:
        if line.startswith(start_char) and secret_value in line:
            # remove +/- in the beginning & spaces and omit
            return omit_secret_value_from_line(secret_value, line[1:].strip()) or ''
    return ''  # not found


def get_secret_key(file_name: str, secret_hash: str, secret_type: str) -> str:
    """
    One way to create a secret key for the secret map
    """
    secret_key = f'{file_name}_{secret_hash}_{secret_type.replace(" ", "-")}'
    return secret_key
