from __future__ import annotations

import os
import shutil
from typing import Any
from pathlib import Path

from checkov.common.runners.base_runner import strtobool
from checkov.common.vcs.base_vcs_dal import BaseVCSDAL
from checkov.github.schemas.org_security import schema as org_security_schema


CKV_METADATA = 'CKV_METADATA'


class Github(BaseVCSDAL):
    github_conf_dir_path: str  # noqa: CCE003  # a static attribute
    github_conf_file_paths: dict[str, list[Path]]  # noqa: CCE003  # a static attribute

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
            "org_security": [Path(self.github_conf_dir_path) / "org_security.json"],
            "branch_protection_rules": [Path(self.github_conf_dir_path) / "branch_protection_rules.json"],
            "org_webhooks": [],  # is updated when persisted
            "repository_webhooks": [],  # is updated when persisted
            "repository_collaborators": [Path(self.github_conf_dir_path) / "repository_collaborators.json"],
            "branch_metadata": [Path(self.github_conf_dir_path) / "branch_metadata.json"],
            "org_metadata": [Path(self.github_conf_dir_path) / "org_metadata.json"],
            "org_admins": [Path(self.github_conf_dir_path) / "org_admins.json"],
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

    # -------------------------------- Endpoints -------------------------------- #

    def get_branch_protection_rules(self) -> dict[str, Any] | None:
        if self.current_branch and self.current_repository:
            data = self._request(
                endpoint=f"repos/{self.repo_owner}/{self.current_repository}/branches/{self.current_branch}/protection",
                allowed_status_codes=[200, 404])
            return data
        return None

    def get_organization_webhooks(self) -> list[dict[str, Any]] | None:
        data = self._request(endpoint=f"orgs/{self.org}/hooks", allowed_status_codes=[200])
        if isinstance(data, list):
            return data
        return None

    def get_repository_collaborators(self) -> dict[str, Any] | None:
        data = self._request(
            endpoint=f"repos/{self.repo_owner}/{self.current_repository}/collaborators",
            allowed_status_codes=[200]
        )
        return data

    def get_repository_webhooks(self) -> list[dict[str, Any]] | None:
        data = self._request(
            endpoint=f"repos/{self.repo_owner}/{self.current_repository}/hooks",
            allowed_status_codes=[200])
        if isinstance(data, list):
            return data
        return None

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

    def get_default_branch(self) -> None:
        # still not used - for future implementations
        default_branch = self.repo_complementary_metadata.get("default_branch")
        if not default_branch:
            data = self._request_graphql(query="""
                query ($owner: String!, $name: String!){
                  repository(owner: $owner, name: $name) {
                    defaultBranchRef {
                      name
                    }
                  }
                }
                """, variables={'owner': self.repo_owner, 'name': self.current_repository})
            if not data:
                return None
            if org_security_schema.validate(data):
                self.repo_complementary_metadata["default_branch"] = \
                    data.get('data', {}).get('repository', {}).get('defaultBranchRef', {}).get('name')

    def get_branch_metadata(self) -> dict[str, Any] | None:
        # new endpoint since Dec22
        data = self._request(
            endpoint=f"repos/{self.repo_owner}/{self.current_repository}/branches/{self.current_branch}",
            allowed_status_codes=[200]
        )
        return data

    def get_organization_metadata(self) -> dict[str, Any] | None:
        # new endpoint since Dec22
        data = self._request(endpoint=f"orgs/{self.org}", allowed_status_codes=[200])
        return data

    def get_organization_admins(self) -> dict[str, Any] | None:
        # new endpoint since Dec22
        data = self._request(endpoint=f"orgs/{self.org}/members?role=admin", allowed_status_codes=[200])
        return data

    def get_repository_metadata(self) -> dict[str, Any] | None:
        # still not used - for future implementations
        data = self._request(
            endpoint=f"repos/{self.repo_owner}/{self.current_repository}",
            allowed_status_codes=[200]
        )
        return data

    # --------------------------------------------------------------------------- #

    def persist_branch_protection_rules(self) -> None:
        data = self.get_branch_protection_rules()
        if data:
            BaseVCSDAL.persist(path=self.github_conf_file_paths["branch_protection_rules"][0], conf=data)

    def persist_organization_security(self) -> None:
        organization_security = self.get_organization_security()
        if organization_security:
            BaseVCSDAL.persist(path=self.github_conf_file_paths["org_security"][0], conf=organization_security)

    def persist_organization_webhooks(self) -> None:
        organization_webhooks = self.get_organization_webhooks()
        if organization_webhooks:
            for idx, item in enumerate(organization_webhooks):
                path = Path(self.github_conf_dir_path) / f"org_webhooks{idx+1}.json"
                self.github_conf_file_paths["org_webhooks"].append(path)
                BaseVCSDAL.persist(path=path, conf=[item])

    def persist_repository_collaborators(self) -> None:
        repository_collaborators = self.get_repository_collaborators()
        if repository_collaborators:
            BaseVCSDAL.persist(
                path=self.github_conf_file_paths["repository_collaborators"][0],
                conf=repository_collaborators)

    def persist_repository_webhooks(self) -> None:
        repository_webhooks = self.get_repository_webhooks()
        if repository_webhooks:
            for idx, item in enumerate(repository_webhooks):
                path = Path(self.github_conf_dir_path) / f"repository_webhooks{idx + 1}.json"
                self.github_conf_file_paths["repository_webhooks"].append(path)
                BaseVCSDAL.persist(path=path, conf=[item])

    def persist_branch_metadata(self) -> None:
        branch_metadata = self.get_branch_metadata()
        if branch_metadata:
            BaseVCSDAL.persist(path=self.github_conf_file_paths["branch_metadata"][0], conf=branch_metadata)

    def persist_organization_metadata(self) -> None:
        org_metadata = self.get_organization_metadata()
        if org_metadata:
            BaseVCSDAL.persist(path=self.github_conf_file_paths["org_metadata"][0], conf=org_metadata)

    def persist_repository_metadata(self) -> None:
        # still not used - for future implementations
        repository_metadata = self.get_repository_metadata()
        if repository_metadata:
            BaseVCSDAL.persist(
                path=self.github_conf_file_paths["repository_metadata"][0],
                conf=repository_metadata
            )
            self.org_complementary_metadata["is_private_repo"] = repository_metadata.get('private')

    def persist_organization_admins(self) -> None:
        org_members = self.get_organization_admins()
        if org_members:
            BaseVCSDAL.persist(path=self.github_conf_file_paths["org_admins"][0], conf=org_members)

    def persist_all_confs(self) -> None:
        if strtobool(os.getenv("CKV_GITHUB_CONFIG_FETCH_DATA", "True")):
            self.persist_organization_security()
            self.persist_branch_protection_rules()
            self.persist_organization_webhooks()
            self.persist_repository_webhooks()
            self.persist_repository_collaborators()
            self.persist_branch_metadata()
            self.persist_organization_metadata()
            self.persist_organization_admins()
