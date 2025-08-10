from __future__ import annotations

import hashlib
import logging
import os
import platform
from typing import TYPE_CHECKING, Optional, List, Tuple, Union

from detect_secrets.core import scan

from checkov.common.util.stopit import ThreadingTimeout, SignalTimeout, TimeoutException
from checkov.common.util.decorators import time_it
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.secrets.consts import GIT_HISTORY_NOT_BEEN_REMOVED
from checkov.secrets.git_history_store import GitHistorySecretStore, RawStore, RENAME_STR, FILE_RESULTS_STR
from checkov.secrets.git_types import Commit, CommitMetadata, PROHIBITED_FILES

if TYPE_CHECKING:
    from detect_secrets import SecretsCollection

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
try:
    from git import Repo, Tree

    git_import_error = None
except ImportError as e:
    git_import_error = e

MIN_SPLIT = 100
FILES_TO_IGNORE_IN_GIT_HISTORY = ('.md', '.svg', '.png', '.jpg') + PROHIBITED_FILES


class GitHistoryScanner:
    commits_count = 0  # noqa: CCE003

    def __init__(self, root_folder: str, secrets: SecretsCollection,
                 history_store: Optional[GitHistorySecretStore] = None, timeout: int = 43200):
        """
        root_folder: Is necessary for initializing the Repo to read from
        secrets: An object which will be filled with secrets during the run of the secrets scan
        history_store: A helper objects which will be field during the run, to map between found secrets and commits.
            is not used afterwards for outside-of-class work
        """
        self.root_folder = root_folder
        self.secrets = secrets
        self.timeout = timeout
        # in case we start from mid-history (git) we want to continue from where we've been
        self.history_store: GitHistorySecretStore = history_store or GitHistorySecretStore()
        self.raw_store: List[RawStore] = []
        self.repo: Repo  # Initialize repo attribute with None

    def scan_history(self, last_commit_scanned: Optional[str] = '', commits_to_scan: Optional[List[Commit]] = None) -> bool:
        """return true if the scan finished without timeout"""
        if not commits_to_scan:
            is_repo_set = self.set_repo()  # for mocking purposes in testing
            if not is_repo_set:
                logging.info("Couldn't set git repo. Cannot proceed with git history scan.")
                return False
        timeout_class = ThreadingTimeout if platform.system() == 'Windows' else SignalTimeout
        # mark the scan to finish within the timeout
        with timeout_class(self.timeout) as to_ctx_mgr:
            scanned = self._scan_history(last_commit_scanned, commits_to_scan)
            self._create_secret_collection()
        if to_ctx_mgr.state == to_ctx_mgr.TIMED_OUT:
            logging.info(f"timeout reached ({self.timeout}), stopping scan.")
            return False
        # else: everything was OK
        return scanned

    @time_it
    def _scan_history(self, last_commit_scanned: Optional[str] = '', commits_to_scan: Optional[List[Commit]] = None) -> bool:
        commits_diff = self.get_commits(last_commit_scanned) if not commits_to_scan else commits_to_scan
        logging.info(f"[_scan_history] got {len(commits_diff)} files diffs in {self.commits_count} commits")
        if self.commits_count > MIN_SPLIT:
            logging.info("[_scan_history] starting parallel scan")
            self._run_scan_parallel(commits_diff)
        else:
            logging.info("[_scan_history] starting single scan")
            self.raw_store.extend(self._run_scan_one_bulk(commits_diff))

        if not self.raw_store:  # scanned nothing
            return False

        self._process_raw_store()
        return True

    def get_commits(self, last_commit_scanned: Optional[str] = '') -> List[Commit]:
        commits_diff: List[Commit] = []
        if not last_commit_scanned:
            first_commit_diff = get_first_commit(self.repo, self.root_folder)
            if first_commit_diff:
                commits_diff.append(first_commit_diff)
        commits_diff.extend(self._get_commits_diff(last_commit_sha=last_commit_scanned))
        return commits_diff

    def _process_raw_store(self) -> None:
        for raw_res in self.raw_store:
            res_type = raw_res.get('type')
            if res_type == FILE_RESULTS_STR:
                self.history_store.set_secret_map(raw_res.get('file_results', []), raw_res.get('file_name', ''),
                                                  raw_res['commit'])
            elif res_type == RENAME_STR:
                self.history_store.handle_renamed_file(raw_res.get('rename_from', ''), raw_res.get('rename_to', ''),
                                                       raw_res['commit'])

    def _create_secret_collection(self) -> None:
        # run over the entire history store and create the secret collection
        for secrets_data in self.history_store.secrets_by_file_value_type.values():
            for secret_data in secrets_data:
                removed = secret_data["removed_commit_hash"] if secret_data[
                    "removed_commit_hash"] else GIT_HISTORY_NOT_BEEN_REMOVED
                key = f'{secret_data["added_commit_hash"]}_{removed}_{secret_data["potential_secret"].filename}'
                self.secrets[key].add(secret_data["potential_secret"])
        logging.info(f"Created secret collection for {len(self.history_store.secrets_by_file_value_type)} secrets")

    def set_repo(self, root_folder: str | None = None) -> bool:
        if not root_folder:
            root_folder = self.root_folder
        if git_import_error is not None:
            logging.warning(f"Unable to load git module (is the git executable available?) {git_import_error}")
            return False
        try:
            self.repo = Repo(root_folder)
            return True
        except Exception as e:
            logging.error(f"Folder {root_folder} is not a GIT project {e}")
            return False

    def _get_commits_diff(self, last_commit_sha: Optional[str] = None) -> List[Commit]:
        """
        :param: last_commit_sha = is the last commit we have already scanned. in case it exist the function will
        return the commits from the revision of param to the current head
        """
        logging.info("[_get_commits_diff] started")
        if last_commit_sha:
            curr_rev = self.repo.head.commit.hexsha
            commits = list(self.repo.iter_commits(last_commit_sha + '..' + curr_rev))
        else:
            commits = list(self.repo.iter_commits(self.repo.active_branch))
        GitHistoryScanner.commits_count = len(commits)
        commits_diff: List[Commit] = []
        for previous_commit_idx in range(GitHistoryScanner.commits_count - 1, 0, -1):
            try:
                current_commit_idx = previous_commit_idx - 1
                current_commit_hash = commits[current_commit_idx].hexsha
                committed_datetime: str = commits[current_commit_idx].committed_datetime.isoformat()
                committer: str = commits[current_commit_idx].committer.name or ''
                git_diff = commits[previous_commit_idx].diff(current_commit_hash, create_patch=True)
                curr_diff: Commit = Commit(
                    metadata=CommitMetadata(
                        commit_hash=current_commit_hash,
                        committer=committer,
                        committed_datetime=committed_datetime
                    )
                )
                for file_diff in git_diff:
                    file_name: str = file_diff.a_path if file_diff.a_path else file_diff.b_path  # type:ignore
                    if file_name.endswith(FILES_TO_IGNORE_IN_GIT_HISTORY):
                        continue
                    file_path = os.path.join(self.root_folder, file_name)

                    if file_diff.renamed_file:
                        logging.debug(f"File was renamed from {file_diff.rename_from} to {file_diff.rename_to}")
                        curr_diff.rename_file(
                            file_path=file_path,
                            prev_filename=file_diff.rename_from or "",
                            new_filename=file_diff.rename_to or ""
                        )
                        continue

                    elif file_diff.deleted_file:
                        logging.debug(f"File {file_diff.a_path} was deleted")

                    base_diff_format = f'diff --git {self.root_folder}/{file_diff.a_path} {self.root_folder}/{file_diff.b_path}' \
                                       f'\nindex 0000..0000 0000\n--- {self.root_folder}/{file_diff.a_path}\n+++ {self.root_folder}/{file_diff.b_path}\n'
                    curr_diff.add_file(filename=file_path,
                                       commit_diff=base_diff_format + get_decoded_diff(file_diff.diff))
                if not curr_diff.is_empty():
                    commits_diff.append(curr_diff)
            except TimeoutException:
                logging.error(f"stopped while getting commits diff, iteration: {previous_commit_idx}")
                return []
            except Exception as err:
                logging.warning(f"got error while getting commits diff, iteration: {previous_commit_idx}, error: {err}")
                continue
        logging.info("[_get_commits_diff] ended")
        return commits_diff

    def _run_scan_parallel(self, commits_diff: List[Commit]) -> None:
        results = parallel_runner.run_function(GitHistoryScanner._run_scan_one_bulk, commits_diff)

        for result in results:
            if result:
                self.raw_store.extend(result)

    @staticmethod
    def _run_scan_one_bulk(commits_diff: List[Commit] | Commit) -> List[RawStore]:
        scanned_file_count = 0
        results: List[RawStore] = []
        # parallel runner can make the list flat, so I can get here dict instead of list
        if isinstance(commits_diff, Commit):
            results, scanned_file_count = GitHistoryScanner._run_scan_one_commit(commits_diff)
        elif isinstance(commits_diff, list):
            for commit in commits_diff:
                cur_results, curr_count = GitHistoryScanner._run_scan_one_commit(commit)
                scanned_file_count += curr_count
                results.extend(cur_results)
        logging.debug(f"Scanned {scanned_file_count} git history files")
        return results

    @staticmethod
    def _run_scan_one_commit(commit: Commit) -> Tuple[List[RawStore], int]:
        results: List[RawStore] = []
        scanned_file_count = 0
        commit_hash = commit.metadata.commit_hash
        for file_name, file_diff in commit.files.items():
            if len(file_diff) == 0:
                continue
            file_results = [*scan.scan_diff(file_diff, commit_hash)]
            if file_results:
                logging.debug(
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
def get_first_commit(repo: Repo, root_folder: str) -> Commit:
    first_commit_sha = repo.git.log('--format=%H', '--max-parents=0', 'HEAD').split()[0]
    first_commit = repo.commit(first_commit_sha)
    empty_tree_sha = bytes.fromhex(hashlib.sha1(b'tree 0\0').hexdigest())  # nosec
    empty_tree = Tree(repo, empty_tree_sha)
    git_diff = empty_tree.diff(first_commit, create_patch=True)

    first_commit_diff: Commit = Commit(
        metadata=CommitMetadata(
            commit_hash=first_commit.hexsha,
            committer=first_commit.committer.name or '',
            committed_datetime=first_commit.committed_datetime.isoformat()
        )
    )

    for file_diff in git_diff:
        file_name: str = file_diff.b_path  # type:ignore
        if file_name.endswith(FILES_TO_IGNORE_IN_GIT_HISTORY):
            continue
        file_path = os.path.join(root_folder, file_name)
        base_diff_format = f"--- ''\n+++ {file_path}\n"
        full_diff_format = base_diff_format + get_decoded_diff(file_diff.diff)
        first_commit_diff.add_file(filename=file_path, commit_diff=full_diff_format)
    return first_commit_diff


def get_decoded_diff(diff: Union[str, bytes, None]) -> str:
    if diff is None:
        return ''

    if isinstance(diff, str):
        return diff

    try:
        decoded_diff = diff.decode('utf-8')
    except UnicodeDecodeError as ue:
        logging.debug(f'failed decoding file diff, {ue}')
        decoded_diff = diff.decode('utf-8', errors='ignore')

    return decoded_diff
