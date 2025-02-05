from __future__ import annotations

import logging
import os
from typing import Any

import requests


class ProxyClient:
    def __init__(self) -> None:
        self.identity = os.getenv('PROXY_HEADER_VALUE')
        self.proxy_ca_path = os.getenv('PROXY_CA_PATH')
        if self.proxy_ca_path is None:
            logging.warning("[ProxyClient] CA certificate path is missing")

    def get_session(self) -> requests.Session:
        if not os.getenv('PROXY_URL'):
            logging.warning('Please provide "PROXY_URL" env var')
        proxy_url = os.getenv('PROXY_URL')
        session = requests.Session()
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
        session.proxies.update(proxies)  # type: ignore
        return session

    def update_request_header(self, request: requests.Request) -> None:
        if os.getenv('PROXY_HEADER_KEY'):
            request.headers[os.getenv('PROXY_HEADER_KEY')] = self.identity

    def send_request(self, request: requests.Request) -> requests.Response:
        session = self.get_session()
        self.update_request_header(request=request)
        prepared_request = session.prepare_request(request)
        return session.send(prepared_request, verify=self.proxy_ca_path)


def call_http_request_with_proxy(request: requests.Request) -> Any:
    proxy_client = ProxyClient()
    return proxy_client.send_request(request=request)
