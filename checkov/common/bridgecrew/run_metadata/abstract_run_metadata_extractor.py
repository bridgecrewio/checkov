from abc import abstractmethod
from checkov.common.bridgecrew.run_metadata.registry import registry
from checkov.common.bridgecrew.run_metadata.ci_variables import (
    BC_TO_BRANCH,
    BC_PR_ID,
    BC_PR_URL,
    BC_COMMIT_HASH,
    BC_COMMIT_URL,
    BC_AUTHOR_NAME,
    BC_AUTHOR_URL,
    BC_RUN_ID,
    BC_RUN_URL,
    BC_REPOSITORY_URL,
    BC_FROM_BRANCH,
)


class RunMetaDataExtractor:
    def __init__(
        self,
        from_branch: str,
        to_branch: str,
        pr_id: str,
        pr_url: str,
        commit_hash: str,
        commit_url: str,
        author_name: str,
        author_url: str,
        run_id: str,
        run_url: str,
        repository_url: str,
    ):
        self.from_branch = from_branch
        self.to_branch = to_branch
        self.pr_id = pr_id
        self.pr_url = pr_url
        self.commit_hash = commit_hash
        self.commit_url = commit_url
        self.author_name = author_name
        self.author_url = author_url
        self.run_id = run_id
        self.run_url = run_url
        self.repository_url = repository_url
        self.override_metadata_from_env_variables()
        registry.register(extractor=self)

    def override_metadata_from_env_variables(self) -> None:
        if BC_FROM_BRANCH:
            self.from_branch = BC_FROM_BRANCH
        if BC_TO_BRANCH:
            self.to_branch = BC_TO_BRANCH
        if BC_PR_ID:
            self.pr_id = BC_PR_ID
        if BC_PR_URL:
            self.pr_url = BC_PR_URL
        if BC_COMMIT_HASH:
            self.commit_hash = BC_COMMIT_HASH
        if BC_COMMIT_URL:
            self.commit_url = BC_COMMIT_URL
        if BC_AUTHOR_NAME:
            self.author_name = BC_AUTHOR_NAME
        if BC_AUTHOR_URL:
            self.author_url = BC_AUTHOR_URL
        if BC_RUN_ID:
            self.run_id = BC_RUN_ID
        if BC_RUN_URL:
            self.run_url = BC_RUN_URL
        if BC_REPOSITORY_URL:
            self.repository_url = BC_REPOSITORY_URL

    @abstractmethod
    def is_current_ci(self) -> bool:
        pass
