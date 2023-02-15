from __future__ import annotations

import git
import logging
from typing import TYPE_CHECKING
from detect_secrets.core import scan
from git import InvalidGitRepositoryError, GitCommandError

if TYPE_CHECKING:
    from detect_secrets import SecretsCollection
    from git import Commit  # type: ignore


def get_commits(root_folder: str) -> list[Commit] | None:
    try:
        repo = git.Repo(root_folder)
    except InvalidGitRepositoryError:
        logging.error(f"Folder {root_folder} is not a GIT project")
        return None
    return list(repo.iter_commits(repo.active_branch))


def scan_history(root_folder: str, secrets: SecretsCollection) -> None:
    commits = get_commits(root_folder)
    if not commits:
        return
    scanned_file_count = 0
    skipped_file_count = 0

    # we scan the diff between the commit and the next commit - start from the end
    for previous_commit_idx in range(len(commits) - 1, 0, -1):
        current_commit_idx = previous_commit_idx - 1
        current_commit_hash = commits[current_commit_idx].hexsha
        git_diff = commits[previous_commit_idx].diff(current_commit_hash, create_patch=True)

        for file_diff in git_diff:
            try:
                if file_diff.renamed:
                    logging.warning(f"File was renamed from {file_diff.rename_from} to {file_diff.rename_to}")
                    pass
                elif file_diff.deleted_file:
                    logging.warning(f"File {file_diff.b_path} was delete")
                    pass
                else:
                    base_diff_format = f'diff --git a/{file_diff.a_path} b/{file_diff.b_path}' \
                                       f'\nindex 0000..0000 0000\n--- a/{file_diff.a_path}\n+++ b/{file_diff.b_path}\n'
                    file_results = [*scan.scan_diff(base_diff_format + file_diff.diff.decode())]
                    if file_results:
                        logging.info(
                            f"Found {len(file_results)} secrets in file path {file_diff.b_path} in commit {current_commit_hash}")
                        logging.info(file_results)
                    for secret in file_results:
                        secrets[
                            f'{current_commit_hash}-{secret.filename}-{secret.secret_hash}-{"added" if secret.is_added else "removed"}'].add(
                            secret)
                    scanned_file_count += 1
            except GitCommandError:
                logging.info(f"File path {file_diff.b_path} does not exist in commit {current_commit_hash}")
                continue
    logging.info(f"Scanned {scanned_file_count} historical files, skipped_file_count {skipped_file_count}")
