import json
import logging
import os
from abc import abstractmethod

import urllib3

from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.http_utils import get_user_agent_header


class BaseVCSDAL:
    def __init__(self):
        self.http = None
        self.request_lib_http = None
        self._organization_security = None
        self.setup_http_manager(ca_certificate=os.getenv('BC_CA_BUNDLE', None))
        self.discover()
        self.setup_conf_dir()

    @abstractmethod
    def discover(self):
        """
            discover parameters from execution context of checkov. usually from env variable
        """
        self.api_url = None
        self.graphql_api_url = None
        self.token = None
        self.current_repository = None
        self.current_branch = None
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

    def _request(self, endpoint):
        if not self.token:
            return
        url_endpoint = "{}/{}".format(self.api_url, endpoint)
        try:
            headers = self._headers()
            request = self.http.request("GET", url_endpoint,
                                        headers=headers)
            if request.status == 200:
                data = json.loads(request.data.decode("utf8"))
                if isinstance(data, dict) and 'errors' in data.keys():
                    return None
                return data
        except Exception:
            logging.debug(f"Query failed to run by returning code of {url_endpoint}", exc_info=True)

    @abstractmethod
    def _headers(self):
        return merge_dicts({"Accept": "application/vnd.github.v3+json",
                            "Authorization": "token {}".format(self.token)}, get_user_agent_header())

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
                    logging.debug("received errors %s", data)
                    return None
                return data

            else:
                logging.debug("Query failed to run by returning code of {}. {}".format(request.data, query))
        except Exception:
            logging.debug(f"Query failed {query}", exc_info=True)

    @staticmethod
    def persist(path, conf):
        BaseVCSDAL.ensure_dir(path)
        with open(path, "w+", encoding='utf-8') as f:
            logging.debug("Persisting to {}".format(path))
            json.dump(conf, f, ensure_ascii=False, indent=4)

    @staticmethod
    def ensure_dir(file_path):
        if not os.path.exists(file_path):
            directory_path = os.path.dirname(file_path)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

    @abstractmethod
    def setup_conf_dir(self):
        pass
