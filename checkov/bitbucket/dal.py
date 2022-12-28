from __future__ import annotations

import logging
import os
from typing import Any

import requests

from checkov.common.runners.base_runner import strtobool
from checkov.common.vcs.base_vcs_dal import BaseVCSDAL


class Bitbucket(BaseVCSDAL):
    def setup_conf_dir(self) -> None:
        """
            discover parameters from execution context of checkov and determine the directory to save temporal files of vcs configuration
        """
        bitbucket_conf_dir_name = os.getenv('CKV_BITBUCKET_CONF_DIR_NAME', 'bitbucket_conf')
        self.bitbucket_conf_dir_path = os.path.join(os.getcwd(), bitbucket_conf_dir_name)
        self.bitbucket_branch_restrictions_file_path = os.path.join(self.bitbucket_conf_dir_path,
                                                                    "branch_restrictions.json")

    def discover(self) -> None:
        """
            discover parameters from execution context of checkov. usually from env variable
        """
        server_host = os.getenv('CI_SERVER_URL', "https://api.bitbucket.org/")
        self.api_url = f'{server_host}2.0'
        self.graphql_api_url = f"{server_host}api/graphql"

        self.token = os.getenv('APP_PASSWORD', '')

        self.current_repository = os.getenv('BITBUCKET_REPO_FULL_NAME', '')
        self.current_branch = os.getenv('BITBUCKET_BRANCH', '')
        self.default_branch_cache = {}
        self.username = os.getenv('BITBUCKET_USERNAME', '')

    def _request(self, endpoint: str, allowed_status_codes: list[int]) -> dict[str, Any] | None:
        if not self.token:
            return None
        url_endpoint = f"{self.api_url}/{endpoint}"
        try:
            s = requests.Session()
            s.auth = (self.username, self.token)
            request = s.get(url_endpoint)
            if request.status_code in allowed_status_codes:
                data: "dict[str, Any]" = request.json()
                if isinstance(data, dict) and 'errors' in data.keys():
                    return None
                return data
            else:
                request.raise_for_status()
        except Exception:
            logging.debug(f"Query failed to run by returning code of {url_endpoint}", exc_info=True)

        return None

    def _headers(self) -> dict[str, Any]:
        # not needed here
        return {}

    def get_branch_restrictions(self) -> dict[str, Any] | None:
        if self.current_repository:
            branch_restrictions = self._request(endpoint=f"repositories/{self.current_repository}/branch-restrictions",
                                                allowed_status_codes=[200])
            return branch_restrictions
        logging.debug("Environment variable BITBUCKET_REPO_FULL_NAME was not set. Cannot fetch branch restrictions.")
        return None

    def persist_branch_restrictions(self) -> None:
        branch_restrictions = self.get_branch_restrictions()

        if branch_restrictions:
            BaseVCSDAL.persist(path=self.bitbucket_branch_restrictions_file_path, conf=branch_restrictions)

    def persist_all_confs(self) -> None:
        if strtobool(os.getenv("CKV_BITBUCKET_CONFIG_FETCH_DATA", "True")):
            self.persist_branch_restrictions()
