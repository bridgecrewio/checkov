from __future__ import annotations

import os
import shutil
from typing import Any
from pathlib import Path

from checkov.common.runners.base_runner import strtobool
from checkov.common.vcs.base_vcs_dal import BaseVCSDAL
from checkov.github.schemas.org_security import schema as org_security_schema


class Github(BaseVCSDAL):
    github_conf_dir_path: str  # noqa: CCE003  # a static attribute
    github_conf_file_paths: dict[str, Path]  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__()

    def setup_conf_dir(self) -> None:
        github_conf_dir_name = os.getenv('CKV_GITHUB_CONF_DIR_NAME', 'github_conf')
        self.github_conf_dir_path = os.path.join(os.getcwd(), github_conf_dir_name)
        os.environ["CKV_GITHUB_CONF_DIR_PATH"] = self.github_conf_dir_path

        # if any file was left from previous run-remove it.
        if os.path.isdir(self.github_conf_dir_path):
            shutil.rmtree(self.github_conf_dir_path)

        self.github_conf_file_paths = {
            "org_security": Path(self.github_conf_dir_path) / "org_security.json",
            "branch_protection_rules": Path(self.github_conf_dir_path) / "branch_protection_rules.json",
            "org_webhooks": Path(self.github_conf_dir_path) / "org_webhooks.json",
            "repository_webhooks": Path(self.github_conf_dir_path) / "repository_webhooks.json",
            "repository_collaborators": Path(self.github_conf_dir_path) / "repository_collaborators.json"
        }

    def discover(self) -> None:
        self.api_url = os.getenv('GITHUB_API_URL', "https://api.github.com")
        self.graphql_api_url = f"{self.api_url}/graphql"

        self.token = os.getenv('GITHUB_TOKEN', '')
        self.repo_owner = os.getenv('GITHUB_REPO_OWNER', '')
        self.current_repository = os.getenv('GITHUB_REPOSITORY', '')
        self.current_branch = os.getenv('GITHUB_REF_NAME', '')
        if not self.current_branch:
            self.current_branch = os.getenv('GITHUB_REF', 'refs/heads/master')
            if self.current_branch:
                extracted_branch_array = self.current_branch.split("/")
                if len(extracted_branch_array) == 3:
                    self.current_branch = extracted_branch_array[2]

        self.default_branch_cache = {}
        self.org = os.getenv('GITHUB_ORG', '')

    def _headers(self) -> dict[str, str]:
        return {"Accept": "application/vnd.github.v3+json",
                "Authorization": "token {}".format(self.token)}

    def get_branch_protection_rules(self) -> dict[str, Any] | None:
        if self.current_branch and self.current_repository:
            branch_protection_rules = self._request(
                endpoint=f"repos/{self.repo_owner}/{self.current_repository}/branches/{self.current_branch}/protection",
                allowed_status_codes=[200, 404])
            return branch_protection_rules
        return None

    def persist_branch_protection_rules(self) -> None:
        data = self.get_branch_protection_rules()
        if data:
            BaseVCSDAL.persist(path=self.github_conf_file_paths["branch_protection_rules"], conf=data)

    def persist_organization_security(self) -> None:
        organization_security = self.get_organization_security()
        if organization_security:
            BaseVCSDAL.persist(path=self.github_conf_file_paths["org_security"], conf=organization_security)

    def persist_organization_webhooks(self) -> None:
        organization_webhooks = self.get_organization_webhooks()
        if organization_webhooks:
            for idx, item in enumerate(organization_webhooks):
                path = str(self.github_conf_file_paths["org_webhooks"])
                BaseVCSDAL.persist(path=path.replace(".json", str(idx) + ".json"), conf=[item])    # type: ignore

    def get_organization_webhooks(self) -> dict[str, Any] | None:
        data = self._request(endpoint="orgs/{}/hooks".format(self.org), allowed_status_codes=[200])
        if not data:
            return None
        return data

    def get_repository_collaborators(self) -> dict[str, Any] | None:
        endpoint = "repos/{}/{}/collaborators".format(self.repo_owner, self.current_repository)
        data = self._request(endpoint=endpoint, allowed_status_codes=[200])
        if not data:
            return None
        return data

    def persist_repository_collaborators(self) -> None:
        repository_collaborators = self.get_repository_collaborators()
        if repository_collaborators:
            BaseVCSDAL.persist(path=self.github_conf_file_paths["repository_collaborators"], conf=repository_collaborators)

    def get_repository_webhooks(self) -> dict[str, Any] | None:
        endpoint = "repos/{}/{}/hooks".format(self.repo_owner, self.current_repository)
        data = self._request(endpoint=endpoint, allowed_status_codes=[200])
        if not data:
            return None
        return data

    def persist_repository_webhooks(self) -> None:
        repository_webhooks = self.get_repository_webhooks()
        if repository_webhooks:
            for idx, item in enumerate(repository_webhooks):
                path = str(self.github_conf_file_paths["repository_webhooks"])
                BaseVCSDAL.persist(path=path.replace(".json", str(idx) + ".json"), conf=[item])    # type: ignore

    def get_organization_security(self) -> dict[str, str] | None:
        if not self._organization_security:
            data = self._request_graphql(query="""
                query ($org: String! ) {
                    organization(login: $org) {
                        name
                        login
                        description
                        ipAllowListEnabledSetting
                        ipAllowListForInstalledAppsEnabledSetting
                        requiresTwoFactorAuthentication
                        samlIdentityProvider {
                            ssoUrl
                        }
                    }
                }
                """, variables={'org': self.org})
            if not data:
                return None
            if org_security_schema.validate(data):
                self._organization_security = data
        return self._organization_security

    def persist_all_confs(self) -> None:
        if strtobool(os.getenv("CKV_GITHUB_CONFIG_FETCH_DATA", "True")):
            self.persist_organization_security()
            self.persist_branch_protection_rules()
            self.persist_organization_webhooks()
            self.persist_repository_webhooks()
            self.persist_repository_collaborators()
