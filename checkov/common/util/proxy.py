import os


class ProxyManager:
    def __init__(self) -> None:
        self.ca_certificate: str | None = None
        self.no_cert_verify: bool = False
        self.proxy_url: str | None = os.getenv('https_proxy')

    def init(self, ca_certificate: str | None, no_cert_verify: bool = False):
        self.ca_certificate = ca_certificate
        self.no_cert_verify = no_cert_verify

        if self.ca_certificate:
            os.environ['REQUESTS_CA_BUNDLE'] = self.ca_certificate

proxy_manager = ProxyManager()