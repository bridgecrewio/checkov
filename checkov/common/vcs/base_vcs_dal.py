from __future__ import annotations

import json
import logging
import os
from abc import abstractmethod
from pathlib import Path
from typing import Any

import urllib3

from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.http_utils import get_user_agent_header


class BaseVCSDAL:
    def __init__(self) -> None:
        self.http: urllib3.PoolManager | None = None
        self.request_lib_http = None
        self._organization_security = None
        self.setup_http_manager(ca_certificate=os.getenv('BC_CA_BUNDLE', None))
        self.discover()
        self.setup_conf_dir()

    @abstractmethod
    def discover(self) -> None:
        """
            discover parameters from execution context of checkov. usually from env variable
        """
        self.api_url = None
        self.graphql_api_url = None
        self.token = None
        self.current_repository = None
        self.current_branch = None
        self.default_branch_cache: dict[str, Any] = {}

    def setup_http_manager(self, ca_certificate: str | None = None) -> None:
        """
        bridgecrew uses both the urllib3 and requests libraries, while checkov uses the requests library.
        :param ca_certificate: an optional CA bundle to be used by both libraries.
        """
        if self.http:
            return
        if ca_certificate:
            os.environ['REQUESTS_CA_BUNDLE'] = ca_certificate
            try:
                parsed_url = urllib3.util.parse_url(os.environ['https_proxy']) # type:ignore[no-untyped-call]
                self.http = urllib3.ProxyManager(os.environ['https_proxy'], cert_reqs='REQUIRED',
                                                 ca_certs=ca_certificate,
                                                 proxy_headers=urllib3.make_headers(proxy_basic_auth=parsed_url.auth)) # type:ignore[no-untyped-call]
            except KeyError:
                self.http = urllib3.PoolManager(cert_reqs='REQUIRED', ca_certs=ca_certificate)
        else:
            try:
                parsed_url = urllib3.util.parse_url(os.environ['https_proxy']) # type:ignore[no-untyped-call]
                self.http = urllib3.ProxyManager(os.environ['https_proxy'],
                                                 proxy_headers=urllib3.make_headers(proxy_basic_auth=parsed_url.auth)) # type:ignore[no-untyped-call]
            except KeyError:
                self.http = urllib3.PoolManager()

    def _request(self, endpoint: str, allowed_status_codes: list[int]) -> dict[str, Any] | None:
        if allowed_status_codes is None:
            allowed_status_codes = [200]
        if not self.token:
            return None
        url_endpoint = f"{self.api_url}/{endpoint}"
        try:
            headers = self._headers()
            request = self.http.request("GET", url_endpoint, headers=headers)
            if request.status in allowed_status_codes:
                data = json.loads(request.data.decode("utf8"))
                if isinstance(data, dict) and 'errors' in data.keys():
                    return None
                return data
        except Exception:
            logging.debug(f"Query failed to run by returning code of {url_endpoint}", exc_info=True)

    @abstractmethod
    def _headers(self) -> dict[str, Any]:
        return merge_dicts({"Accept": "application/vnd.github.v3+json",
                            "Authorization": f"token {self.token}"}, get_user_agent_header())

    def _graphql_headers(self) -> dict[str, str]:
        return {"Authorization": f"bearer {self.token}"}

    def _request_graphql(self, query: str, variables: dict[str, Any]) -> Any:
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
    def persist(path: str | Path, conf: dict[str, Any]) -> None:
        BaseVCSDAL.ensure_dir(path)
        with open(path, "w+", encoding='utf-8') as f:
            logging.debug(f"Persisting to {path}")
            json.dump(conf, f, ensure_ascii=False, indent=4)

    @staticmethod
    def ensure_dir(file_path: str | Path) -> None:
        if not os.path.exists(file_path):
            directory_path = os.path.dirname(file_path)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

    @abstractmethod
    def setup_conf_dir(self) -> None:
        pass
