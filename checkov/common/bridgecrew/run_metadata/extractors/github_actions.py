import os

from checkov.common.bridgecrew.run_metadata.abstract_run_metadata_extractor import RunMetaDataExtractor


class GithubActionsRunMetadataExtractor(RunMetaDataExtractor):
    def is_current_ci(self) -> bool:
        if os.getenv("GITHUB_ACTIONS", ""):
            return True
        return False

    def __init__(self) -> None:
        server_url = os.getenv('GITHUB_SERVER_URL', '')
        from_branch = os.getenv('GIT_BRANCH', "master")
        to_branch = os.getenv('GITHUB_BASE_REF', "")
        pr_id = os.getenv("$GITHUB_REF", "//").split("/")[2]
        repository = os.getenv('GITHUB_REPOSITORY', "")
        pr_url = f"{server_url}/{repository}/pull/{pr_id}"
        commit_hash = os.getenv("GITHUB_SHA", "")
        commit_url = f"{server_url}/{repository}/commit/${commit_hash}"
        author_name = os.getenv("GITHUB_ACTOR", "")
        author_url = f"{server_url}/{author_name}"
        run_id = os.getenv("GITHUB_RUN_NUMBER", "")
        run_url = f"{server_url}/{repository}/actions/runs/{run_id}"
        repository_url = f"{server_url}/{repository}"

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


extractor = GithubActionsRunMetadataExtractor()
