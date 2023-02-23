from __future__ import annotations

import copy
import logging
import os
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Tuple, List
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


def get_commits_diff(root_folder: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
    commits_diff: Dict[str, Dict[str, str | Dict[str, str]]] = {}
    if git_import_error is not None:
        logging.warning(f"Unable to load git module (is the git executable available?) {git_import_error}")
        return commits_diff
    try:
        repo = git.Repo(root_folder)
    except Exception as e:
        logging.error(f"Folder {root_folder} is not a GIT project {e}")
        return commits_diff
    commits = list(repo.iter_commits(repo.active_branch))
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


def scan_history(root_folder: str, secrets: SecretsCollection, timeout: int = 43200) -> bool:
    """return true if the scan finished without timeout"""
    # mark the scan to finish within the timeout
    with stopit.ThreadingTimeout(timeout) as to_ctx_mgr:
        commits_diff = get_commits_diff(root_folder)
        if commits_diff:
            scanned_file_count = 0
            # the secret key will be {file name}_{hash_value}_{type}
            secret_map: Dict[str, List[EnrichedPotentialSecret]] = {}
            for commit_hash in commits_diff.keys():
                commit = commits_diff[commit_hash]
                for file_name in commit.keys():
                    file_diff = commit[file_name]
                    if isinstance(file_diff, str):
                        file_results = [*scan.scan_diff(file_diff)]
                        if file_results:
                            logging.info(
                                f"Found {len(file_results)} secrets in file path {file_name} in commit {commit_hash}")
                            logging.info(file_results)
                            set_secret_map(file_results, secret_map, file_name, commit_hash)
                    elif isinstance(file_diff, dict):
                        rename_from = file_diff['rename_from']
                        rename_to = file_diff['rename_to']
                        handle_renamed_file(rename_from, rename_to, secret_map, commit_hash)
                    scanned_file_count += 1
            for secrets_data in secret_map.values():
                for secret_data in secrets_data:
                    removed = secret_data["removed_commit_hash"] if secret_data[
                        "removed_commit_hash"] else GIT_HISTORY_NOT_BEEN_REMOVED
                    key = f'{secret_data["added_commit_hash"]}_{removed}_{secret_data["potential_secret"].filename}'
                    secrets[key].add(secret_data["potential_secret"])
            logging.info(f"Scanned {scanned_file_count} git history files")
    if to_ctx_mgr.state == to_ctx_mgr.TIMED_OUT:
        logging.info(f"timeout reached ({timeout}), stopping scan.")
        return False
    # else: everything was OK
    return True


def set_secret_map(file_results: List[PotentialSecret], secret_map: Dict[str, List[EnrichedPotentialSecret]],
                   file_name: str, commit_hash: str) -> None:
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
            add_new_secret_to_map(secret_key, secret_map, commit_hash, secret)
        if secret.is_removed:
            update_removed_secret_in_map(secret_key, secret_map, commit_hash, secret, file_name)


def add_new_secret_to_map(secret_key: str,
                          secret_map: Dict[str, List[EnrichedPotentialSecret]],
                          commit_hash: str,
                          secret: PotentialSecret) -> None:
    if secret_key not in secret_map:
        secret_map[secret_key] = []
    else:
        all_removed = all(
            potential_secret.get('removed_commit_hash') for potential_secret in secret_map[secret_key])
        # Update secret map with the new potential secret
        if all_removed:
            secret_map[secret_key][0].update({'potential_secret': secret, 'removed_commit_hash': ''})
            return
    secret_map[secret_key].append(
        {'added_commit_hash': commit_hash, 'removed_commit_hash': '', 'potential_secret': secret})


def update_removed_secret_in_map(secret_key: str,
                                 secret_map: Dict[str, List[EnrichedPotentialSecret]],
                                 commit_hash: str,
                                 secret: PotentialSecret,
                                 file_name: str) -> None:
    # Try to find the corresponding added secret in the git history secret map
    try:
        for secret_in_file in secret_map[secret_key]:
            if secret_in_file['potential_secret'].is_added:
                secret_in_file['removed_commit_hash'] = commit_hash
                secret_in_file['potential_secret'] = secret
                break
    except KeyError:
        logging.error(f"No added secret commit found for secret in file {file_name}.")


def handle_renamed_file(rename_from: str,
                        rename_to: str,
                        secret_map: Dict[str, List[EnrichedPotentialSecret]],
                        commit_hash: str) -> None:
    temp_map: Dict[str, List[EnrichedPotentialSecret]] = {}
    for secret_key in secret_map.keys():
        if rename_from in secret_key:
            new_secret_key = secret_key.replace(rename_from, rename_to)
            temp_map[new_secret_key] = []
            secret_in_file = secret_map[secret_key]
            for secret_data in secret_in_file:
                # defines the secret in the old file as removed and add the secret to the new file
                secret_data['removed_commit_hash'] = commit_hash
                new_secret = copy.deepcopy(secret_data['potential_secret'])
                new_secret.filename = rename_to
                temp_map[new_secret_key].append({'added_commit_hash': commit_hash,
                                                   'removed_commit_hash': '',
                                                   'potential_secret': new_secret})
    secret_map.update(temp_map)


def get_added_and_removed_commit_hash(
        key: str, enable_git_history_secret_scan: bool) -> Tuple[str | None, str | None]:
    """
    now we have only the current commit_hash - in the added_commit_hash or in the removed_commit_hash.
    in the next step we will add the connection and the missing data
    The key is built like this:
    '{added_commit_hash}_{removed_commit_hash or the string SECRET_NOT_BEEN_REMOVED if the secret not been removed}_{file_name}'
    """
    if not enable_git_history_secret_scan:
        return None, None
    split_key = key.split('_')
    added_commit_hash = split_key[0]
    removed_commit_hash = split_key[1] if split_key[1] != GIT_HISTORY_NOT_BEEN_REMOVED else None
    return added_commit_hash, removed_commit_hash
