import json
import logging
import os

import urllib3

from checkov.common.runners.base_runner import strtobool
from checkov.github.schemas.org_security import schema as org_security_schema


class Github:
    def __init__(self):
        self.http = None
        self._organization_security = None
        self.setup_http_manager(ca_certificate=os.getenv('BC_CA_BUNDLE', None))
        self.discover()
        self.configure_github_conf_dir()

    def configure_github_conf_dir(self):
        # files downloaded from github will be persistent in this directory
        github_conf_dir_name = os.getenv('CKV_GITHUB_CONF_DIR_NAME', 'github_conf')
        self.github_conf_dir_path = os.path.join(os.getcwd(), github_conf_dir_name)
        self.github_org_security_file_path = os.path.join(self.github_conf_dir_path, "org_security.json")
        self.github_branch_protection_rules_file_path = os.path.join(self.github_conf_dir_path,
                                                                     "branch_protection_rules.json")

    def discover(self):

        self.api_url = os.getenv('GITHUB_API_URL', "https://api.github.com/")
        self.graphql_api_url = f"{self.api_url}graphql"

        self.token = os.getenv('GITHUB_TOKEN', '')

        self.current_repository = os.getenv('GITHUB_REPOSITORY', '')
        self.current_branch = os.getenv('GITHUB_REF_NAME', '')

        self.default_branch_cache = {}

    def setup_http_manager(self, ca_certificate=None):
        """
        bridgecrew uses both the urllib3 and requests libraries, while checkov uses the requests library.
        :param ca_certificate: an optional CA bundle to be used by both libraries.
        """
        if self.http:
            return
        if ca_certificate:
            os.environ['REQUESTS_CA_BUNDLE'] = ca_certificate
            try:
                self.http = urllib3.ProxyManager(os.environ['https_proxy'], cert_reqs='REQUIRED',
                                                 ca_certs=ca_certificate)
            except KeyError:
                self.http = urllib3.PoolManager(cert_reqs='REQUIRED', ca_certs=ca_certificate)
        else:
            try:
                self.http = urllib3.ProxyManager(os.environ['https_proxy'])
            except KeyError:
                self.http = urllib3.PoolManager()

    def _authenticate(self):
        pass

    def _request(self, endpoint):
        if not self.token:
            return
        url_endpoint = "{}{}".format(self.api_url, endpoint)
        try:
            request = self.http.request("GET", url_endpoint,
                                        headers=self._headers())
            if request.status == 200:
                data = json.loads(request.data.decode("utf8"))
                if isinstance(data, dict) and 'errors' in data.keys():
                    return None
                return data
        except Exception:
            logging.debug("Query failed to run by returning code of {}.".format(url_endpoint))

    def _headers(self):
        return {"Accept": "application/vnd.github.v3+json",
                "Authorization": "token {}".format(self.token)}

    def _graphql_headers(self):
        return {
            "Authorization": "bearer {}".format(self.token)}

    def _request_graphql(self, query, variables):
        if not self.token:
            return
        headers = self._graphql_headers()

        body = json.dumps({'query': query, 'variables': variables})
        try:
            request = self.http.request("POST", self.graphql_api_url, body=body, headers=headers)
            if request.status == 200:
                data = json.loads(request.data.decode("utf8"))
                if isinstance(data, dict) and 'errors' in data.keys():
                    return None
                return data

            else:
                logging.debug("Query failed to run by returning code of {}. {}".format(request.data, query))
        except Exception as e:
            logging.debug("Quer y failed {} exception {}.".format(query, e))


    def get_branch_protection_rules(self):
        if self.current_branch and self.current_repository:
            branch_protection_rules = self._request(
                endpoint="repos/{}/branches/{}/protection".format(self.current_repository, self.current_branch))
            return branch_protection_rules
        return None

    def persist_branch_protection_rules(self):
        data = self.get_branch_protection_rules()
        if data:
            Github.persist(path=self.github_branch_protection_rules_file_path, conf=data)

    def persist_organization_security(self):
        organization_security = self.get_organization_security()
        if organization_security:
            Github.persist(path=self.github_org_security_file_path, conf=organization_security)

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
                """, variables={'org': 'bridgecrewio'})
            if org_security_schema.validate(data):
                self._organization_security = data
        return self._organization_security

    def persist_all_confs(self):
        if strtobool(os.getenv("CKV_GITHUB_CONFIG_FETCH_DATA", "True")):
            self.persist_organization_security()
            self.persist_branch_protection_rules()

    @staticmethod
    def persist(path, conf):
        Github.ensure_dir(path)
        with open(path, "w+", encoding='utf-8') as f:
            logging.debug("Persisting to {}".format(path))
            json.dump(conf, f, ensure_ascii=False, indent=4)

    @staticmethod
    def ensure_dir(file_path):
        if not os.path.exists(file_path):
            directory_path = os.path.dirname(file_path)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
