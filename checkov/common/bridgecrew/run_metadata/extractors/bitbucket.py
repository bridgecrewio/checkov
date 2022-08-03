import os

from checkov.common.bridgecrew.run_metadata.abstract_run_metadata_extractor import RunMetaDataExtractor


class BitbucketRunMetadataExtractor(RunMetaDataExtractor):
    def is_current_ci(self) -> bool:
        if os.getenv("BITBUCKET_BUILD_NUMBER", "") and os.getenv("CI", ""):
            return True
        return False

    def __init__(self) -> None:
        from_branch = os.getenv('BITBUCKET_BRANCH', "master")
        to_branch = os.getenv('BITBUCKET_PR_DESTINATION_BRANCH', "")
        pr_id = os.getenv("BITBUCKET_PR_ID", "")
        pr_url = ""
        commit_hash = os.getenv("BITBUCKET_COMMIT", "")
        repository_url = os.getenv("BITBUCKET_GIT_HTTP_ORIGIN","")
        commit_url = ""
        author_name = ""
        author_url = ""
        run_id = os.getenv("BITBUCKET_BUILD_NUMBER", "")
        run_url = ""

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


extractor = BitbucketRunMetadataExtractor()
