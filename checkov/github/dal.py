from __future__ import annotations

import os
from typing import Any

from checkov.common.runners.base_runner import strtobool
from checkov.common.vcs.base_vcs_dal import BaseVCSDAL
from checkov.github.schemas.org_security import schema as org_security_schema


class Github(BaseVCSDAL):

    def __init__(self) -> None:
        super().__init__()
        self.github_conf_dir_path: str
        self.github_org_security_file_path: str
        self.github_branch_protection_rules_file_path: str
        self.github_org_webhooks_file_path: str
        self.github_repository_webhooks_file_path: str
        self.github_repository_collaborators_file_path: str

    def setup_conf_dir(self) -> None:
        # files downloaded from github will be persistent in this directory
        github_conf_dir_name = os.getenv('CKV_GITHUB_CONF_DIR_NAME', 'github_conf')
        self.github_conf_dir_path = os.path.join(os.getcwd(), github_conf_dir_name)
        self.github_org_security_file_path = os.path.join(self.github_conf_dir_path, "org_security.json")
        self.github_branch_protection_rules_file_path = os.path.join(self.github_conf_dir_path,
                                                                     "branch_protection_rules.json")
        self.github_org_webhooks_file_path = os.path.join(self.github_conf_dir_path,
                                                          "org_webhooks.json")
        self.github_repository_webhooks_file_path = os.path.join(self.github_conf_dir_path,
                                                                 "repository_webhooks.json")
        self.github_repository_collaborators_file_path = os.path.join(self.github_conf_dir_path,
                                                                      "repository_collaborators.json")

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
            BaseVCSDAL.persist(path=self.github_branch_protection_rules_file_path, conf=data)

    def persist_organization_security(self) -> None:
        organization_security = self.get_organization_security()
        if organization_security:
            BaseVCSDAL.persist(path=self.github_org_security_file_path, conf=organization_security)

    def persist_organization_webhooks(self) -> None:
        organization_webhooks = self.get_organization_webhooks()
        if organization_webhooks:
            BaseVCSDAL.persist(path=self.github_org_webhooks_file_path, conf=organization_webhooks)

    def get_organization_webhooks(self) -> dict[str, Any] | None:
        data = self._request(endpoint="orgs/{}/hooks".format(self.org), allowed_status_codes=[200])
        if not data:
            return None
        return data

    def get_repository_collaborators(self) -> dict[str, Any] | None:
        data = self._request(endpoint="repos/{}/{}/collaborators".format(self.org, self.current_repository),
                             allowed_status_codes=[200])
        if not data:
            return None
        return data

    def persist_repository_collaborators(self) -> None:
        repository_collaborators = self.get_repository_collaborators()
        if repository_collaborators:
            BaseVCSDAL.persist(path=self.github_repository_collaborators_file_path, conf=repository_collaborators)

    def get_repository_webhooks(self) -> dict[str, Any] | None:
        data = self._request(endpoint="repos/{}/{}/hooks".format(self.org, self.current_repository),
                             allowed_status_codes=[200])
        if not data:
            return None
        return data

    def persist_repository_webhooks(self) -> None:
        repository_webhooks = self.get_repository_webhooks()
        if repository_webhooks:
            BaseVCSDAL.persist(path=self.github_repository_webhooks_file_path, conf=repository_webhooks)

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
