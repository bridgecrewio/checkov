from __future__ import annotations

import logging
from typing import Any

import requests

from checkov.common.util.env_vars_config import env_vars_config


class ProxyClient:
    def __init__(self) -> None:
        self.identity = env_vars_config.PROXY_HEADER_VALUE
        self.proxy_ca_path = env_vars_config.PROXY_CA_PATH
        if self.proxy_ca_path is None:
            logging.warning("[ProxyClient] CA certificate path is missing")

    def get_session(self) -> requests.Session:
        if not env_vars_config.PROXY_URL:
            logging.warning('Please provide "PROXY_URL" env var')
        proxy_url = env_vars_config.PROXY_URL
        session = requests.Session()
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
        session.proxies.update(proxies)  # type: ignore
        return session

    def update_request_header(self, request: requests.Request) -> None:
        if env_vars_config.PROXY_HEADER_VALUE:
            request.headers[env_vars_config.PROXY_HEADER_VALUE] = self.identity

    def send_request(self, request: requests.Request) -> requests.Response:
        session = self.get_session()
        self.update_request_header(request=request)
        prepared_request = session.prepare_request(request)
        return session.send(prepared_request, verify=self.proxy_ca_path)


def call_http_request_with_proxy(request: requests.Request) -> Any:
    proxy_client = ProxyClient()
    return proxy_client.send_request(request=request)
