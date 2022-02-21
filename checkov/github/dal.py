import os

from checkov.common.runners.base_runner import strtobool
from checkov.common.vcs.base_vcs_dal import BaseVCSDAL
from checkov.github.schemas.org_security import schema as org_security_schema


class Github(BaseVCSDAL):
    def __init__(self):
        super().__init__()

    def setup_conf_dir(self):
        # files downloaded from github will be persistent in this directory
        github_conf_dir_name = os.getenv('CKV_GITHUB_CONF_DIR_NAME', 'github_conf')
        self.github_conf_dir_path = os.path.join(os.getcwd(), github_conf_dir_name)
        self.github_org_security_file_path = os.path.join(self.github_conf_dir_path, "org_security.json")
        self.github_branch_protection_rules_file_path = os.path.join(self.github_conf_dir_path,
                                                                     "branch_protection_rules.json")

    def discover(self):

        self.api_url = os.getenv('GITHUB_API_URL', "https://api.github.com")
        self.graphql_api_url = f"{self.api_url}/graphql"

        self.token = os.getenv('GITHUB_TOKEN', '')

        self.current_repository = os.getenv('GITHUB_REPOSITORY', '')
        self.current_branch = os.getenv('GITHUB_REF_NAME', '')
        if not self.current_branch:
            self.current_branch = os.getenv('GITHUB_REF', '')
            if self.current_branch:
                extracted_branch_array = self.current_branch.split("/")
                if len(extracted_branch_array) == 3:
                    self.current_branch = extracted_branch_array[2]

        self.default_branch_cache = {}
        self.org = os.getenv('GITHUB_ORG', '')

    def _headers(self):
        return {"Accept": "application/vnd.github.v3+json",
                "Authorization": "token {}".format(self.token)}

    def get_branch_protection_rules(self):
        if self.current_branch and self.current_repository:
            branch_protection_rules = self._request(
                endpoint="repos/{}/branches/{}/protection".format(self.current_repository, self.current_branch))
            return branch_protection_rules
        return None

    def persist_branch_protection_rules(self):
        data = self.get_branch_protection_rules()
        if data:
            BaseVCSDAL.persist(path=self.github_branch_protection_rules_file_path, conf=data)

    def persist_organization_security(self):
        organization_security = self.get_organization_security()
        if organization_security:
            BaseVCSDAL.persist(path=self.github_org_security_file_path, conf=organization_security)

    def get_organization_security(self):
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
            if org_security_schema.validate(data):
                self._organization_security = data
        return self._organization_security

    def persist_all_confs(self):
        if strtobool(os.getenv("CKV_GITHUB_CONFIG_FETCH_DATA", "True")):
            self.persist_organization_security()
            self.persist_branch_protection_rules()
