import os

from checkov.common.bridgecrew.run_metadata.abstract_run_metadata_extractor import AbsRunMetaDataExtractor


class GithubActionsAbsRunMetadataExtractor(AbsRunMetaDataExtractor):
    def is_current_ci(self):
        if os.getenv("GITHUB_ACTIONS", ""):
            return True
        return False

    def __init__(self):
        github_server_url = os.getenv('GITHUB_SERVER_URL', '')
        from_branch = os.getenv('GIT_BRANCH', "master")
        to_branch = os.getenv('GITHUB_BASE_REF', "")
        pr_id = os.getenv("$GITHUB_REF", "//").split("/")
        github_repsitory = os.getenv('GITHUB_REPOSITORY', "")
        pr_url = f"{github_server_url}/{github_repsitory}/pull/{pr_id}"
        commit_hash = os.getenv("GITHUB_SHA", "")
        commit_url = f"{github_server_url}/{github_repsitory}/commit/${commit_hash}"
        author_name = os.getenv("GITHUB_ACTOR", "")
        author_url = f"{github_server_url}/{author_name}"
        run_id = os.getenv("GITHUB_RUN_NUMBER", "")
        run_url = f"{github_server_url}/{github_repsitory}/actions/runs/{run_id}"
        repository_url = f"{github_server_url}/{github_repsitory}"

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


extractor = GithubActionsAbsRunMetadataExtractor()
