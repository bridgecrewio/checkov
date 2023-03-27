from __future__ import annotations

import logging
import copy
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Tuple, Optional
from typing_extensions import TypedDict
from checkov.secrets.consts import ADDED, REMOVED, GIT_HISTORY_OPTIONS, GIT_HISTORY_NOT_BEEN_REMOVED

if TYPE_CHECKING:
    from detect_secrets.core.potential_secret import PotentialSecret


class EnrichedPotentialSecret(TypedDict):
    added_commit_hash: str
    removed_commit_hash: str
    potential_secret: PotentialSecret
    code_line: Optional[str]


class GitHistorySecretStore:
    def __init__(self) -> None:
        self.secrets_by_file_value_type: Dict[str, List[EnrichedPotentialSecret]] = {}

    def set_secret_map(self, file_results: List[PotentialSecret],
                       file_name: str, commit_hash: str, commit: Dict[str, str | Dict[str, str]]) -> None:
        # First find if secret was moved in the file
        equal_secret_in_commit: Dict[str, List[str]] = defaultdict(list)
        for secret in file_results:
            secret_key = get_secret_key(file_name, secret.secret_hash, secret.type)
            equal_secret_in_commit[secret_key].append(ADDED if secret.is_added else REMOVED)

        for secret in file_results:
            if secret.filename in ['None', '']:
                secret.filename = file_name
            secret_key = get_secret_key(file_name, secret.secret_hash, secret.type)
            if all(value in equal_secret_in_commit[secret_key] for value in GIT_HISTORY_OPTIONS):
                continue
            if secret.is_added:
                self._add_new_secret(secret_key, commit_hash, secret, commit)
            if secret.is_removed:
                self._update_removed_secret(secret_key, secret, file_name, commit_hash)

    def _add_new_secret(self, secret_key: str,
                        commit_hash: str,
                        secret: PotentialSecret,
                        commit: Dict[str, str | Dict[str, str]]) -> None:
        if secret_key not in self.secrets_by_file_value_type:
            self.secrets_by_file_value_type[secret_key] = []
        else:
            all_removed = all(
                potential_secret.get('removed_commit_hash') for potential_secret in
                self.secrets_by_file_value_type[secret_key])
            # Update secret map with the new potential secret
            if all_removed:
                self.secrets_by_file_value_type[secret_key][0].update(
                    {'potential_secret': secret, 'removed_commit_hash': ''})
                return
        code_line = search_for_code_line(commit[secret.filename], secret.secret_value, secret.is_added)
        self.secrets_by_file_value_type[secret_key].append(
            {'added_commit_hash': commit_hash,
             'removed_commit_hash': '',
             'potential_secret': secret,
             'code_line': code_line
             })

    def _update_removed_secret(self, secret_key: str,
                               secret: PotentialSecret,
                               file_name: str,
                               commit_hash: str) -> None:
        # Try to find the corresponding added secret in the git history secret map
        secrets_in_file = self.secrets_by_file_value_type.get(secret_key, None)
        if secrets_in_file:
            for secret_in_file in secrets_in_file:
                if secret_in_file['potential_secret'].is_added:
                    secret_in_file['removed_commit_hash'] = commit_hash
                    secret_in_file['potential_secret'] = secret
                    break
        else:
            logging.error(f"No added secret commit found for secret in file {file_name}.")

    def handle_renamed_file(self, rename_from: str,
                            rename_to: str,
                            commit_hash: str) -> None:
        temp_secrets_by_file_value_type: Dict[str, List[EnrichedPotentialSecret]] = {}
        for secret_key in self.secrets_by_file_value_type.keys():
            if rename_from in secret_key:
                new_secret_key = secret_key.replace(rename_from, rename_to)
                temp_secrets_by_file_value_type[new_secret_key] = []
                secret_in_file = self.secrets_by_file_value_type[secret_key]
                for secret_data in secret_in_file:
                    # defines the secret in the old file as removed and add the secret to the new file
                    secret_data['removed_commit_hash'] = commit_hash
                    new_secret = copy.deepcopy(secret_data['potential_secret'])
                    new_secret.filename = rename_to
                    code = secret_data.get('code_line')
                    temp_secrets_by_file_value_type[new_secret_key].append({'added_commit_hash': commit_hash,
                                                                            'removed_commit_hash': '',
                                                                            'potential_secret': new_secret,
                                                                            'code_line': code})
        self.secrets_by_file_value_type.update(temp_secrets_by_file_value_type)

    def get_added_and_removed_commit_hash(self, key: str, secret: PotentialSecret) -> \
            Tuple[str | None, str | None, str | None]:
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
            enriched_secrets = self.secrets_by_file_value_type[secret_key]
            chosen_secret = enriched_secrets[0]
            if len(enriched_secrets) > 1:
                added, removed, _file = key.split("_")
                if removed == GIT_HISTORY_NOT_BEEN_REMOVED:
                    removed = ''
                for enriched_secret in enriched_secrets:
                    if added == enriched_secret.get('added_commit_hash') and \
                            removed == enriched_secret.get('removed_commit_hash'):
                        chosen_secret = enriched_secret
                        break

            added_commit_hash = chosen_secret.get('added_commit_hash')
            removed_commit_hash = chosen_secret.get('removed_commit_hash') or None
            code = chosen_secret.get('code_line')
            return added_commit_hash, removed_commit_hash, code
        except Exception as e:
            logging.warning(f"Failed set added_commit_hash and removed_commit_hash due to: {e}")
            return None, None, None


def search_for_code_line(commit: str | Dict[str, str], secret_value: Optional[str], is_added: Optional[bool]) -> str:
    if secret_value is None:
        return ''
    if isinstance(commit, dict):
        return ''  # no need to support rename
    splitted = commit.split('\n')
    start_char = '+' if is_added else '-'
    for line in splitted:
        if line.startswith(start_char) and secret_value in line:
            return line[1:].strip()  # remove +/- in the beginning & spaces
    return ''  # not found


def get_secret_key(file_name: str, secret_hash: str, secret_type: str) -> str:
    """
    One way to create a secret key for the secret map
    """
    secret_key = f'{file_name}_{secret_hash}_{secret_type.replace(" ", "-")}'
    return secret_key
