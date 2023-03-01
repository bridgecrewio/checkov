from __future__ import annotations

import copy
import logging
import os
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List
from checkov.common.util import stopit
from detect_secrets.core import scan
from typing_extensions import TypedDict

from checkov.secrets.consts import GIT_HISTORY_NOT_BEEN_REMOVED

if TYPE_CHECKING:
    from detect_secrets import SecretsCollection
    from detect_secrets.core.potential_secret import PotentialSecret

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
try:
    import git

    git_import_error = None
except ImportError as e:
    git_import_error = e


class EnrichedPotentialSecret(TypedDict):
    added_commit_hash: str
    removed_commit_hash: str
    potential_secret: PotentialSecret


class GitHistoryScanner:
    def __init__(self, root_folder: str, secrets: SecretsCollection, timeout: int = 43200):
        self.root_folder = root_folder
        self.secrets = secrets
        self.timeout = timeout
        self.secret_store = GitHistorySecretStore()

    def scan_history(self) -> bool:
        """return true if the scan finished without timeout"""
        # mark the scan to finish within the timeout
        with stopit.ThreadingTimeout(self.timeout) as to_ctx_mgr:
            commits_diff = self._get_commits_diff()
            if commits_diff:
                scanned_file_count = 0
                # the secret key will be {file name}_{hash_value}_{type}
                for commit_hash in commits_diff.keys():
                    commit = commits_diff[commit_hash]
                    for file_name in commit.keys():
                        file_diff = commit[file_name]
                        if isinstance(file_diff, str):
                            file_results = [*scan.scan_diff(file_diff)]
                            if file_results:
                                logging.info(
                                    f"Found {len(file_results)} secrets in file path {file_name} in commit {commit_hash}, file_results = {file_results}")

                                self.secret_store.set_secret_map(file_results, file_name, commit_hash)
                        elif isinstance(file_diff, dict):
                            rename_from = file_diff['rename_from']
                            rename_to = file_diff['rename_to']
                            self.secret_store.handle_renamed_file(rename_from, rename_to, commit_hash)
                        scanned_file_count += 1
                for secrets_data in self.secret_store.secrets_by_file_value_type.values():
                    for secret_data in secrets_data:
                        removed = secret_data["removed_commit_hash"] if secret_data[
                            "removed_commit_hash"] else GIT_HISTORY_NOT_BEEN_REMOVED
                        key = f'{secret_data["added_commit_hash"]}_{removed}_{secret_data["potential_secret"].filename}'
                        self.secrets[key].add(secret_data["potential_secret"])
                logging.info(f"Scanned {scanned_file_count} git history files")
        if to_ctx_mgr.state == to_ctx_mgr.TIMED_OUT:
            logging.info(f"timeout reached ({self.timeout}), stopping scan.")
            return False
        # else: everything was OK
        return True

    def _get_commits_diff(self) -> Dict[str, Dict[str, str | Dict[str, str]]]:
        commits_diff: Dict[str, Dict[str, str | Dict[str, str]]] = {}
        if git_import_error is not None:
            logging.warning(f"Unable to load git module (is the git executable available?) {git_import_error}")
            return commits_diff
        try:
            repo = git.Repo(self.root_folder)
        except Exception as e:
            logging.error(f"Folder {self.root_folder} is not a GIT project {e}")
            return commits_diff
        commits = list(repo.iter_commits(repo.active_branch, max_count=2))
        for previous_commit_idx in range(len(commits) - 1, 0, -1):
            current_commit_idx = previous_commit_idx - 1
            current_commit_hash = commits[current_commit_idx].hexsha
            git_diff = commits[previous_commit_idx].diff(current_commit_hash, create_patch=True)

            for file_diff in git_diff:
                if file_diff.renamed:
                    logging.info(f"File was renamed from {file_diff.rename_from} to {file_diff.rename_to}")
                    commits_diff.setdefault(current_commit_hash, {})
                    commits_diff[current_commit_hash][file_diff.a_path] = {
                        'rename_from': file_diff.rename_from,
                        'rename_to': file_diff.rename_to
                    }
                    continue
                elif file_diff.deleted_file:
                    logging.info(f"File {file_diff.b_path} was delete")

                base_diff_format = f'diff --git a/{file_diff.a_path} b/{file_diff.b_path}' \
                                   f'\nindex 0000..0000 0000\n--- a/{file_diff.a_path}\n+++ b/{file_diff.b_path}\n'
                commits_diff.setdefault(current_commit_hash, {})
                commits_diff[current_commit_hash][file_diff.a_path] = base_diff_format + file_diff.diff.decode()
        return commits_diff


class GitHistorySecretStore:
    def __init__(self) -> None:
        self.secrets_by_file_value_type: Dict[str, List[EnrichedPotentialSecret]] = {}

    def set_secret_map(self, file_results: List[PotentialSecret], file_name: str, commit_hash: str) -> None:
        # First find if secret was moved in the file
        equal_secret_in_commit: Dict[str, List[str]] = defaultdict(list)
        for secret in file_results:
            secret_key = f'{file_name}_{secret.secret_hash}_{secret.type.replace(" ", "-")}'
            equal_secret_in_commit[secret_key].append('added' if secret.is_added else 'removed')

        for secret in file_results:
            secret_key = f'{file_name}_{secret.secret_hash}_{secret.type.replace(" ", "-")}'
            if all(value in equal_secret_in_commit[secret_key] for value in ['added', 'removed']):
                continue
            if secret.is_added:
                self._add_new_secret(secret_key, commit_hash, secret)
            if secret.is_removed:
                self._update_removed_secret(secret_key, secret, file_name, commit_hash)

    def _add_new_secret(self, secret_key: str,
                        commit_hash: str,
                        secret: PotentialSecret) -> None:
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
        self.secrets_by_file_value_type[secret_key].append(
            {'added_commit_hash': commit_hash, 'removed_commit_hash': '', 'potential_secret': secret})

    def _update_removed_secret(self, secret_key: str,
                               secret: PotentialSecret,
                               file_name: str,
                               commit_hash: str) -> None:
        # Try to find the corresponding added secret in the gitz t history secret map
        try:
            for secret_in_file in self.secrets_by_file_value_type[secret_key]:
                if secret_in_file['potential_secret'].is_added:
                    secret_in_file['removed_commit_hash'] = commit_hash
                    secret_in_file['potential_secret'] = secret
                    break
        except KeyError:
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
                    temp_secrets_by_file_value_type[new_secret_key].append({'added_commit_hash': commit_hash,
                                                                            'removed_commit_hash': '',
                                                                            'potential_secret': new_secret})
        self.secrets_by_file_value_type.update(temp_secrets_by_file_value_type)
