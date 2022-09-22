from __future__ import annotations

import os
from typing import Any

from checkov.common.runners.base_runner import strtobool
from checkov.common.vcs.base_vcs_dal import BaseVCSDAL


class Gitlab(BaseVCSDAL):
    def __init__(self) -> None:
        super().__init__()

    def setup_conf_dir(self) -> None:
        """
            discover parameters from execution context of checkov and determine the directory to save temporal files of vcs configuration
        """
        gitlab_conf_dir_name = os.getenv('CKV_GITLAB_CONF_DIR_NAME', 'gitlab_conf')
        self.gitlab_conf_dir_path = os.path.join(os.getcwd(), gitlab_conf_dir_name)
        self.gitlab_project_approvals_file_path = os.path.join(self.gitlab_conf_dir_path,
                                                               "project_approvals.json")
        self.gitlab_groups_file_path = os.path.join(self.gitlab_conf_dir_path,
                                                    "groups.json")

    def discover(self) -> None:
        """
            discover parameters from execution context of checkov. usually from env variable
        """
        server_host = os.getenv('CI_SERVER_URL', "https://gitlab.com")
        self.api_url = f'{server_host}/api/v4/'
        self.graphql_api_url = f"{server_host}/api/graphql"

        self.token = os.getenv('CI_JOB_TOKEN', '')

        self.current_repository = os.getenv('CI_MERGE_REQUEST_PROJECT_PATH', '')
        self.current_branch = os.getenv('CI_COMMIT_REF_NAME', '')
        self.group_name = os.getenv('CI_PROJECT_NAMESPACE', '')
        self.project_id = os.getenv('CI_PROJECT_ID', '')
        self.default_branch_cache = {}

    def _headers(self) -> dict[str, str]:
        return {"Authorization": "Bearer {}".format(self.token)}

    def get_project_approvals(self) -> dict[str, Any] | None:
        if self.project_id:
            project_approvals = self._request(endpoint=f"projects/{self.project_id}/approvals",
                                              allowed_status_codes=[200])
            return project_approvals
        return None

    def persist_project_approvals(self) -> None:
        project_approvals = self.get_project_approvals()

        if project_approvals:
            BaseVCSDAL.persist(path=self.gitlab_project_approvals_file_path, conf=project_approvals)

    def get_groups(self) -> dict[str, Any] | None:
        groups = self._request(endpoint="groups", allowed_status_codes=[200])
        return groups

    def persist_groups(self) -> None:
        groups = self.get_groups()
        if groups:
            BaseVCSDAL.persist(path=self.gitlab_groups_file_path, conf=groups)

    def persist_all_confs(self) -> None:
        if strtobool(os.getenv("CKV_GITLAB_CONFIG_FETCH_DATA", "True")):
            self.persist_project_approvals()
            self.persist_groups()
