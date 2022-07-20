import os

from checkov.common.bridgecrew.run_metadata.abstract_run_metadata_extractor import RunMetaDataExtractor


class JenkinsRunMetadataExtractor(RunMetaDataExtractor):
    def is_current_ci(self) -> bool:
        if os.getenv("JENKINS_URL", ""):
            return True
        return False

    def __init__(self) -> None:
        server_url = os.getenv('JENKINS_URL', '')
        from_branch = os.getenv('ghprbSourceBranch', "master")
        to_branch = os.getenv('ghprbTargetBranch', "")
        pr_id = os.getenv("ghprbPullId", "")
        pr_url = os.getenv("ghprbPullLink", "")
        commit_hash = os.getenv("ghprbActualCommit", "")
        repository_url = server_url
        commit_url = server_url
        author_name = os.getenv("ghprbActualCommitAuthor", "")
        author_url = server_url
        run_id = os.getenv("BUILD_NUMBER", "")
        run_url = os.getenv("BUILD_URL", "")

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


extractor = JenkinsRunMetadataExtractor()
