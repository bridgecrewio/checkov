from __future__ import annotations

import base64
import os
import shutil
from typing import Any
from pathlib import Path

from checkov.common.runners.base_runner import strtobool
from checkov.common.vcs.base_vcs_dal import BaseVCSDAL


class AzureDevOps(BaseVCSDAL):
    def __init__(self) -> None:
        super().__init__()
        self.conf_dir_path: Path
        self.conf_file_paths: dict[str, list[Path]]

    def setup_conf_dir(self) -> None:
        conf_dir_name = os.getenv("CKV_AZURE_DEVOPS_CONF_DIR_NAME", "azure_devops_conf")
        self.conf_dir_path = Path.cwd() / conf_dir_name

        # if any file was left from previous run-remove it.
        if self.conf_dir_path.is_dir():
            shutil.rmtree(self.conf_dir_path)

        self.conf_file_paths = {
            "policies": [self.conf_dir_path / "policies.json"],
        }

    def discover(self) -> None:
        self.api_url = os.getenv(
            "SYSTEM_COLLECTIONURI", f"https://dev.azure.com/{os.getenv('SYSTEM_COLLECTIONNAME', '')}"
        )
        self.token = os.getenv("SYSTEM_ACCESSTOKEN", "")

        self.org_id = os.getenv("SYSTEM_COLLECTIONID", "")
        self.project_name = os.getenv("SYSTEM_TEAMPROJECT", "")
        self.project_id = os.getenv("SYSTEM_TEAMPROJECTID", "")
        self.repository_name = os.getenv("BUILD_REPOSITORY_NAME", "")
        self.repository_id = os.getenv("BUILD_REPOSITORY_ID", "")
        self.branch = os.getenv("SYSTEM_PULLREQUEST_TARGETBRANCH", "")

        self.api_version_query = "api-version=7.0"  # 7.1 is not GA
        self.default_branch_cache = {}

    def _headers(self) -> dict[str, str]:
        b64_token = base64.b64encode(f":{self.token}".encode("utf-8")).decode("utf-8")
        return {
            "Authorization": f"Basic {b64_token}",
        }

    # -------------------------------- Endpoints -------------------------------- #

    def get_policies(self) -> dict[str, Any] | None:
        if self.repository_id and self.branch:
            data = self._request(
                endpoint=f"{self.project_name}/_apis/git/policy/configurations?{self.api_version_query}&repositoryId={self.repository_id}&refName={self.branch}",
                allowed_status_codes=[200],
            )
            return data
        return None

    # --------------------------------------------------------------------------- #

    def persist_policies(self) -> None:
        data = self.get_policies()
        if data and data.get("count") and "value" in data:
            BaseVCSDAL.persist(path=self.conf_file_paths["policies"][0], conf=data["value"])

    def persist_all_confs(self) -> None:
        if strtobool(os.getenv("CKV_AZURE_DEVOPS_CONFIG_FETCH_DATA", "True")):
            self.persist_policies()
