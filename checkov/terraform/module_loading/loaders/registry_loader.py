import os
from http import HTTPStatus
from typing import List, Dict

import requests

from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.loader import ModuleLoader
from checkov.terraform.module_loading.loaders.versions_parser import (
    order_versions_in_descending_order,
    get_version_constraints,
)


class RegistryLoader(ModuleLoader):
    REGISTRY_URL_PREFIX = "https://registry.terraform.io/v1/modules"

    modules_versions_cache: Dict[str, List[str]] = {}

    def __init__(self) -> None:
        super().__init__()
        self.module_version_url = ""

    def _is_matching_loader(self) -> bool:
        # Since the registry loader is the first one to be checked,
        # it shouldn't process any github modules
        if self.module_source.startswith(("github.com", "bitbucket.org")):
            return False

        self._process_inner_registry_module()
        if os.path.exists(self.dest_dir):
            return True

        self.module_version_url = "/".join((self.REGISTRY_URL_PREFIX, self.module_source, "versions"))
        if not self.module_version_url.startswith(self.REGISTRY_URL_PREFIX):
            # Local paths don't get the prefix appended
            return False
        if self.module_version_url in RegistryLoader.modules_versions_cache.keys():
            return True

        response = requests.get(url=self.module_version_url)
        if response.status_code != HTTPStatus.OK:
            return False
        else:
            available_versions = [
                v.get("version") for v in response.json().get("modules", [{}])[0].get("versions", {})
            ]
            RegistryLoader.modules_versions_cache[self.module_version_url] = order_versions_in_descending_order(available_versions)
            return True

    def _load_module(self) -> ModuleContent:
        if os.path.exists(self.dest_dir):
            return ModuleContent(dir=self.dest_dir)

        best_version = self._find_best_version()

        request_download_url = "/".join((self.REGISTRY_URL_PREFIX, self.module_source, best_version, "download"))
        response = requests.get(url=request_download_url)
        if response.status_code != HTTPStatus.OK and response.status_code != HTTPStatus.NO_CONTENT:
            return ModuleContent(dir=None)
        else:
            return ModuleContent(dir=None, next_url=response.headers.get("X-Terraform-Get", ""))

    def _find_module_path(self) -> str:
        # to determine the exact path here would be almost a duplicate of the git_loader functionality
        return ""

    def _find_best_version(self) -> str:
        versions_by_size = RegistryLoader.modules_versions_cache.get(self.module_version_url, [])
        if self.version == "latest":
            self.version = versions_by_size[0]
        version_constraints = get_version_constraints(self.version)
        num_of_matches = 0
        for version in versions_by_size:
            for version_constraint in version_constraints:
                if not version_constraint.versions_matching(version):
                    break
                else:
                    num_of_matches += 1
            if num_of_matches == len(version_constraints):
                return version
            else:
                num_of_matches = 0
        return "latest"

    def _process_inner_registry_module(self) -> None:
        # Check if the source has '//' in it. If it does, it indicates a reference for an inner module.
        # Example: "terraform-aws-modules/security-group/aws//modules/http-80" =>
        #    module_source = terraform-aws-modules/security-group/aws
        #    dest_dir = modules/http-80
        module_source_components = self.module_source.split("//")
        if len(module_source_components) > 1:
            self.module_source = module_source_components[0]
            self.dest_dir = self.dest_dir.split("//")[0]
            self.inner_module = module_source_components[1]


loader = RegistryLoader()
