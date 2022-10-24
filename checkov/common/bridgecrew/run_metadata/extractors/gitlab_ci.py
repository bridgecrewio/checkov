import os

from checkov.common.bridgecrew.run_metadata.abstract_run_metadata_extractor import RunMetaDataExtractor


class GitLabRunMetadataExtractor(RunMetaDataExtractor):
    def is_current_ci(self) -> bool:
        if os.getenv("GITLAB_CI", ""):
            return True
        return False

    def __init__(self) -> None:
        server_url = os.getenv('CI_SERVER_URL', '')
        from_branch = os.getenv('GIT_BRANCH', "master")
        to_branch = os.getenv('CI_MERGE_REQUEST_TARGET_BRANCH_NAME', "")
        pr_id = os.getenv("CI_MERGE_REQUEST_ID", "")
        pr_url = os.getenv("CI_MERGE_REQUEST_PROJECT_URL", "")
        commit_hash = os.getenv("CI_COMMIT_SHORT_SHA", "")
        repository_url = os.getenv("CI_PROJECT_URL", "")
        long_commit_hash = os.getenv("CI_COMMIT_SHA", "")
        commit_url = f"{repository_url}/-/commit/${long_commit_hash}"
        author_name = os.getenv("CI_COMMIT_AUTHOR", "")
        author_url = f"{server_url}/{author_name}"
        run_id = os.getenv("CI_PIPELINE_ID", "")
        run_url = os.getenv("CI_PIPELINE_URL", "")

        super().__init__(from_branch=from_branch,
                         to_branch=to_branch,
                         pr_id=pr_id,
                         pr_url=pr_url,
                         commit_hash=commit_hash,
                         commit_url=commit_url,
                         author_name=author_name,
                         author_url=author_url,
                         run_id=run_id,
                         run_url=run_url,
                         repository_url=repository_url)


extractor = GitLabRunMetadataExtractor()
