import os

import urllib3

from checkov.common.runners.base_runner import strtobool
from checkov.common.vcs.base_vcs_dal import BaseVCSDAL


class Bitbucket(BaseVCSDAL):
    def __init__(self):
        super().__init__()

    def setup_conf_dir(self):
        """
            discover parameters from execution context of checkov and determine the directory to save temporal files of vcs configuration
        """
        bitbucket_conf_dir_name = os.getenv('CKV_BITBUCKET_CONF_DIR_NAME', 'bitbucket_conf')
        self.bitbucket_conf_dir_path = os.path.join(os.getcwd(), bitbucket_conf_dir_name)
        self.bitbucket_branch_restrictions_file_path = os.path.join(self.bitbucket_conf_dir_path,
                                                               "project_approvals.json")


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
            branch_restrictions = self._request(
                endpoint=f"repositories/{self.current_repository}/branch-restrictions")
            return branch_restrictions
        return None

    def persist_branch_restrictions(self):
        branch_restrictions = self.get_branch_restrictions()

        if branch_restrictions:
            BaseVCSDAL.persist(path=self.bitbucket_branch_restrictions_file_path, conf=branch_restrictions)

    def persist_all_confs(self):
        if strtobool(os.getenv("CKV_BITBUCKET_CONFIG_FETCH_DATA", "True")):
            self.persist_branch_restrictions()


bb = Bitbucket()
b = bb.get_branch_restrictions()
print (b)