from checkov.common.bridgecrew.run_metadata.abstract_run_metadata_extractor import RunMetaDataExtractor


class DefaultRunMetadataExtractor(RunMetaDataExtractor):
    def is_current_ci(self) -> bool:
        return False

    def __init__(self) -> None:
        from_branch = ""
        to_branch = ""
        pr_id = ""
        pr_url = ""
        commit_hash = ""
        repository_url = ""
        commit_url = ""
        author_name = ""
        author_url = ""
        run_id = ""
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


extractor = DefaultRunMetadataExtractor()
