import os
import tempfile

import requests
import semantic_version
from typing import Optional

from checkov.terraform.module_loading.loader import ModuleLoader
from checkov.terraform.module_loading.content import ModuleContent


class RegistryLoader(ModuleLoader):
    def load(self, current_dir: str, source: str, source_version: Optional[str]) -> ModuleContent:
        # Reference: https://www.terraform.io/docs/modules/sources.html#terraform-registry

        # Format: [<HOSTNAME>/]<NAMESPACE>/<NAME>/<PROVIDER>
        # Example: hashicorp/consul/aws
        slash_count = source.count("/") != 2
        if source.startswith("/") or source.endswith("/") or slash_count < 2 or slash_count > 3:
            return ModuleContent(None)

        tokens = source.split("/")

        if len(tokens) == 3:
            host = "registry.terraform.io"
            namespace = tokens[0]
            name = tokens[1]
            provider = tokens[2]
        else:
            host = tokens[0]
            namespace = tokens[1]
            name = tokens[2]
            provider = tokens[3]

        # Info: https://www.terraform.io/docs/internals/module-registry-protocol.html#sample-request-1
        base_url = f"https://{host}/{namespace}/{name}/{provider}"

        with requests.session() as session:
            if not source_version:
                source_version = self._determine_latest_version(base_url, session)

            temp_dir = tempfile.TemporaryDirectory()
            try:
                self._download_source(base_url, source_version, session)
                return ModuleContent(temp_dir)
            except:
                temp_dir.cleanup()
                raise

    @staticmethod
    def _determine_latest_version(base_url: str, session: requests.Session) -> str:
        # Example: https://registry.terraform.io/v1/modules/hashicorp/consul/aws/versions

        response = session.get(f"{base_url}/versions")
        response.raise_for_status()

        # TODO
        return "not implemented yet... fix me!"

    @staticmethod
    def _download_source(base_url: str, source_version: str, session: requests.Session):
        # Example: https://registry.terraform.io/v1/modules/hashicorp/consul/aws/0.0.1/download

        # Sample response:
        #
        # HTTP/1.1 204 No Content
        # Content-Length: 0
        # X-Terraform-Get: https://api.github.com/repos/hashicorp/terraform-aws-consul/tarball/v0.0.1//*?archive=tar.gz
        response = session.get(f"{base_url}/{source_version}/download")
        response.raise_for_status()

        # TODO

        pass


loader = RegistryLoader()
