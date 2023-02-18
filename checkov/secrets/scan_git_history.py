from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Dict
from detect_secrets.core import scan

if TYPE_CHECKING:
    from detect_secrets import SecretsCollection

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
try:
    import git
    git_import_error = None
except ImportError as e:
    git_import_error = e


def get_commits_diff(root_folder: str) -> Dict[str, Dict[str, str]]:
    commits_diff: Dict[str, Dict[str, str]] = {}
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
                logging.warning(f"File was renamed from {file_diff.rename_from} to {file_diff.rename_to}")
                pass
            elif file_diff.deleted_file:
                logging.warning(f"File {file_diff.b_path} was delete")
                pass
            else:
                base_diff_format = f'diff --git a/{file_diff.a_path} b/{file_diff.b_path}' \
                                   f'\nindex 0000..0000 0000\n--- a/{file_diff.a_path}\n+++ b/{file_diff.b_path}\n'
                commits_diff.setdefault(current_commit_hash, {})
                commits_diff[current_commit_hash][file_diff.a_path] = base_diff_format + file_diff.diff.decode()
    return commits_diff


def scan_history(root_folder: str, secrets: SecretsCollection) -> None:
    commits_diff = get_commits_diff(root_folder)
    if not commits_diff:
        return
    scanned_file_count = 0
    for commit_hash in commits_diff.keys():
        commit = commits_diff[commit_hash]
        for file_name in commit.keys():
            file_diff = commit[file_name]
            file_results = [*scan.scan_diff(file_diff)]
            if file_results:
                logging.info(
                    f"Found {len(file_results)} secrets in file path {file_name} in commit {commit_hash}")
                logging.info(file_results)
            for secret in file_results:
                secrets[
                    f'{commit_hash}-{secret.filename}-{secret.secret_hash}-{"added" if secret.is_added else "removed"}'].add(secret)
            scanned_file_count += 1
    logging.info(f"Scanned {scanned_file_count} git history files")
