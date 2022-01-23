import os

import urllib3
from requests.auth import HTTPBasicAuth

from checkov.common.runners.base_runner import strtobool
from checkov.common.vcs.base_vcs_dal import BaseVCSDAL

import re

class Bitbucket(BaseVCSDAL):
    def __init__(self):
        super().__init__()

    def setup_conf_dir(self):
        """
            discover parameters from execution context of checkov and determine the directory to save temporal files of vcs configuration
        """
        bitbucket_conf_dir_name = os.getenv('CKV_BITBUCKET_CONF_DIR_NAME', 'bitbucket_conf')
        self.bitbucket_conf_dir_path = os.path.join(os.getcwd(), bitbucket_conf_dir_name)
        self.bitbucket_project_approvals_file_path = os.path.join(self.bitbucket_conf_dir_path,
                                                               "project_approvals.json")
        self.bitbucket_groups_file_path = os.path.join(self.bitbucket_conf_dir_path,
                                                    "groups.json")

    def discover(self):
        """
            discover parameters from execution context of checkov. usually from env variable
        """
        server_host = os.getenv('CI_SERVER_URL', "http://api.bitbucket.org/")
        self.api_url = f'{server_host}/2.0/'
        self.graphql_api_url = f"{server_host}/api/graphql"

        self.token = os.getenv('APP_PASSWORD', '')

        self.current_repository = os.getenv('BITBUCKET_REPO_FULL_NAME', '')
        self.current_branch = os.getenv('BITBUCKET_BRANCH', '')
        self.group_name = os.getenv('BITBUCKET_WORKSPACE', '')
        self.project_id = os.getenv('BITBUCKET_REPO_UUID', '')
        self.username = os.getenv('BITBUCKET_USERNAME', '')
        self.default_branch_cache = {}

    def _headers(self):
        return urllib3.make_headers(basic_auth=f'{self.username}:{self.token}')

    def get_branch_restrictions(self):
        if self.project_id:
            project_approvals = self._request(
                endpoint=f"repositories/{self.current_repository}/branch-restrictions")
            return project_approvals
        return None

    def persist_project_approvals(self):
        project_approvals = self.get_branch_restrictions()

        if project_approvals:
            BaseVCSDAL.persist(path=self.bitbucket_project_approvals_file_path, conf=project_approvals)

    def get_groups(self):
        groups = self._request(
            endpoint="groups")
        return groups

    def persist_groups(self):
        groups = self.get_groups()
        if groups:
            BaseVCSDAL.persist(path=self.bitbucket_groups_file_path, conf=groups)


    def persist_all_confs(self):
        if strtobool(os.getenv("CKV_BITBUCKET_CONFIG_FETCH_DATA", "True")):
            self.persist_project_approvals()
            self.persist_groups()


bb = Bitbucket()
b = bb.get_branch_restrictions()
print (b)