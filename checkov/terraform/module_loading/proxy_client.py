import os
from typing import Any

import requests
from requests import Request

PROXY_DOME_HEADER = 'X-Proxydome-Identity'


class ProxyClient:
    def __init__(self) -> None:
        self._identity: str = os.getenv('IDENTITY_PROVIDER', None)
        self.proxy_ca_path = os.getenv('EGRESSPROXY_CA_PATH', None)
        if self.proxy_ca_path is None:
            raise Exception("[ProxyClient] CA certificate path is missing")

    def get_session(self) -> requests.Session:
        if not self.proxy_dome_enabled():
            raise Exception("Proxy dome is disabled")

        session = requests.Session()
        proxy_url = self.get_proxy()
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
        session.proxies.update(proxies)
        return session

    def update_request_header(self, request: requests.Request) -> None:
        request.headers[PROXY_DOME_HEADER] = self._identity

    def send_request(self, request: requests.Request) -> requests.Response:
        session = self.get_session()
        self.update_request_header(request=request)
        prepared_request = session.prepare_request(request)
        return session.send(prepared_request, verify=self.proxy_ca_path)

    def proxy_dome_enabled(self) -> bool:
        return 'EGRESSPROXY_URL' in os.environ

    def get_proxy(self) -> str:
        proxy_url = os.getenv('EGRESSPROXY_URL')
        if proxy_url is None:
            raise ValueError("EGRESSPROXY_URL environment variable is not set")
        return f"http://{proxy_url}"


def call_http_request_with_proxy(request: Request) -> Any:
    proxy_client = ProxyClient()
    return proxy_client.send_request(request=request)