from __future__ import annotations

import logging
import os

from typing import TYPE_CHECKING, Optional, List, Tuple
from checkov.common.util.stopit import ThreadingTimeout
from checkov.common.util.decorators import time_it
from checkov.common.parallelizer.parallel_runner import parallel_runner
from detect_secrets.core import scan

from checkov.secrets.git_history_store import GitHistorySecretStore, RawStore, RENAME_STR, FILE_RESULTS_STR
from checkov.secrets.git_types import Commit, CommitMetadata, GIT_HISTORY_NOT_BEEN_REMOVED

if TYPE_CHECKING:
    from detect_secrets import SecretsCollection

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
try:
    import git

    git_import_error = None
except ImportError as e:
    git_import_error = e

MIN_SPLIT = 100

FILES_TO_IGNORE_IN_GIT_HISTORY = ('.md',)

@time_it
def _get_commits_diff(root_folder: str, last_commit_sha: Optional[str] = None) -> List[Commit]:
    """
    :param: last_commit_sha = is the last commit we have already scanned. in case it exist the function will
    return the commits from the revision of param to the current head
    """
    logging.info("[_get_commits_diff] started")
    commits_diff: List[Commit] = []
    if git_import_error is not None:
        logging.warning(f"Unable to load git module (is the git executable available?) {git_import_error}")
        return commits_diff
    try:
        repo = git.Repo(root_folder)
    except Exception as e:
        logging.error(f"Folder {root_folder} is not a GIT project {e}")
        return commits_diff
    if last_commit_sha:
        curr_rev = repo.head.commit.hexsha
        commits = list(repo.iter_commits(last_commit_sha + '..' + curr_rev))
    else:
        commits = list(repo.iter_commits(repo.active_branch))
    for previous_commit_idx in range(len(commits) - 1, 0, -1):
        try:

            current_commit_idx = previous_commit_idx - 1
            current_commit_hash = commits[current_commit_idx].hexsha
            committed_datetime: str = commits[current_commit_idx].committed_datetime.isoformat()
            committer: str = commits[current_commit_idx].committer.name or ''
            git_diff = commits[previous_commit_idx].diff(current_commit_hash, create_patch=True)

            for file_diff in git_diff:
                file_name = file_diff.a_path if file_diff.a_path else file_diff.b_path
                if file_name.endswith(FILES_TO_IGNORE_IN_GIT_HISTORY):
                    continue
                curr_diff: Commit = Commit(
                    metadata=CommitMetadata(
                        commit_hash=current_commit_hash,
                        committer=committer,
                        committed_datetime=committed_datetime
                    )
                )
                if file_diff.renamed_file:
                    logging.debug(f"File was renamed from {file_diff.rename_from} to {file_diff.rename_to}")
                    curr_diff.rename_file(
                        file_path=file_diff.a_path,
                        prev_filename=file_diff.rename_from,
                        new_filename=file_diff.rename_to
                    )
                    commits_diff.append(curr_diff)
                    continue

                elif file_diff.deleted_file:
                    logging.debug(f"File {file_diff.a_path} was deleted")

                base_diff_format = f'diff --git a/{file_diff.a_path} b/{file_diff.b_path}' \
                                   f'\nindex 0000..0000 0000\n--- a/{file_diff.a_path}\n+++ b/{file_diff.b_path}\n'
                file_name = file_diff.a_path if file_diff.a_path else file_diff.b_path
                curr_diff.add_file(filename=file_name, commit_diff=base_diff_format + file_diff.diff.decode())
                commits_diff.append(curr_diff)
        except Exception as e:
            logging.warning(f"got error while getting commits diff, iteration: {previous_commit_idx}, error: {e}")
            continue
    logging.info("[_get_commits_diff] ended")
    return commits_diff


def _scan_history(
        root_folder: str,
        secret_store: SecretsCollection,
        history_store: GitHistorySecretStore,
        last_commit_scanned: Optional[str] = ''
) -> None:
    commits_diff = _get_commits_diff(root_folder, last_commit_sha=last_commit_scanned)
    if not commits_diff:
        return
    logging.info(f"[_scan_history] got {len(commits_diff)} commits to scan")
    raw_store: List[RawStore]
    if len(commits_diff) > MIN_SPLIT:
        logging.info("[_scan_history] starting parallel scan")
        raw_store = _run_scan_parallel(commits_diff)
    else:
        logging.info("[_scan_history] starting single scan")
        raw_store = _run_scan_one_bulk(commits_diff)

    _process_raw_store(history_store, raw_store)

    _create_secret_collection(secret_store, history_store)


@time_it
def _process_raw_store(base_history_store: GitHistorySecretStore, results: List[RawStore]) -> None:
    for raw_res in results:
        res_type = raw_res.get('type')
        if res_type == FILE_RESULTS_STR:
            base_history_store.set_secret_map(raw_res.get('file_results', []), raw_res.get('file_name', ''), raw_res['commit'])
        elif res_type == RENAME_STR:
            base_history_store.handle_renamed_file(raw_res.get('rename_from', ''), raw_res.get('rename_to', ''), raw_res['commit'])


def _run_scan_parallel(commits_diff: List[Commit]) -> List[RawStore]:
    results = parallel_runner.run_function(_run_scan_one_bulk, commits_diff)

    final_results: List[RawStore] = []
    for result in results:
        if not result:
            continue
        final_results.extend(result)
    return final_results


def _run_scan_one_bulk(commits_diff: List[Commit] | Commit) -> List[RawStore]:
    scanned_file_count = 0
    results: List[RawStore] = []
    # parallel runner can make the list flat, so I can get here dict instead of list
    if isinstance(commits_diff, Commit):
        results, scanned_file_count = _run_scan_one_commit(commits_diff)
    elif isinstance(commits_diff, list):
        for commit in commits_diff:
            cur_results, curr_count = _run_scan_one_commit(commit)
            scanned_file_count += curr_count
            results.extend(cur_results)
    logging.debug(f"Scanned {scanned_file_count} git history files")
    return results


def _run_scan_one_commit(commit: Commit) -> Tuple[List[RawStore], int]:
    results: List[RawStore] = []
    scanned_file_count = 0
    commit_hash = commit.metadata.commit_hash
    for file_name, file_diff in commit.files.items():
        file_results = [*scan.scan_diff(file_diff)]
        if file_results:
            logging.info(
                f"Found {len(file_results)} secrets in file path {file_name} in commit {commit_hash}")
            results.append(RawStore(file_results=file_results, file_name=file_name, commit=commit,
                                    type=FILE_RESULTS_STR, rename_from='', rename_to=''))
    for _, details in commit.renamed_files.items():
        rename_from = details['rename_from']
        rename_to = details['rename_to']
        results.append(RawStore(file_results=[], file_name='', commit=commit, type=RENAME_STR,
                                rename_from=rename_from, rename_to=rename_to))
        scanned_file_count += 1
    return results, scanned_file_count


@time_it
def _create_secret_collection(
        secret_store: SecretsCollection, history_store: GitHistorySecretStore) -> None:
    # run over the entire history store and create the secret collection
    for secrets_data in history_store.secrets_by_file_value_type.values():
        for secret_data in secrets_data:
            removed = secret_data["removed_commit_hash"] if secret_data["removed_commit_hash"] else GIT_HISTORY_NOT_BEEN_REMOVED
            key = f'{secret_data["added_commit_hash"]}_{removed}_{secret_data["potential_secret"].filename}'
            secret_store[key].add(secret_data["potential_secret"])
    logging.info(f"Created secret collection for {len(history_store.secrets_by_file_value_type)} secrets")


class GitHistoryScanner:
    def __init__(self, root_folder: str, secrets: SecretsCollection,
                 history_store: Optional[GitHistorySecretStore] = None, timeout: int = 43200):
        self.root_folder = root_folder
        self.secrets = secrets
        self.timeout = timeout
        # in case we start from mid-history (git) we want to continue from where we've been
        self.history_store = history_store or GitHistorySecretStore()

    def scan_history(self, last_commit_scanned: Optional[str] = '') -> bool:
        """return true if the scan finished without timeout"""
        # mark the scan to finish within the timeout
        with ThreadingTimeout(self.timeout) as to_ctx_mgr:
            _scan_history(self.root_folder, self.secrets, self.history_store, last_commit_scanned)
        if to_ctx_mgr.state == to_ctx_mgr.TIMED_OUT:
            logging.info(f"timeout reached ({self.timeout}), stopping scan.")
            return False
        # else: everything was OK
        return True