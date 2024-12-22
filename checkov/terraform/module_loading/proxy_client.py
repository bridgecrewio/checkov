import os
from typing import Any

import requests


class ProxyClient:
    def __init__(self) -> None:
        self.proxy_ca_path = os.getenv('PROXY_CA_PATH', None)
        if self.proxy_ca_path is None:
            raise Exception("[ProxyClient] CA certificate path is missing")

    def get_session(self) -> requests.Session:
        if not os.getenv('PROXY_URL', None):
            raise Exception('Please provide "PROXY_URL" env var')
        proxy_url = os.getenv('PROXY_URL')
        session = requests.Session()
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
        session.proxies.update(proxies)
        return session

    def send_request(self, request: requests.Request) -> requests.Response:
        session = self.get_session()
        prepared_request = session.prepare_request(request)
        return session.send(prepared_request, verify=self.proxy_ca_path)


def call_http_request_with_proxy(request: requests.Request) -> Any:
    proxy_client = ProxyClient()
    return proxy_client.send_request(request=request)
