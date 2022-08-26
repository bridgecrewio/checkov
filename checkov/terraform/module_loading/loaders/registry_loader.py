import os
import logging
from http import HTTPStatus
from typing import List, Dict

import requests
from requests.exceptions import HTTPError

from checkov.common.models.consts import TFC_HOST_NAME
from checkov.common.goget.registry.get_registry import RegistryGetter
from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.loader import ModuleLoader
from checkov.terraform.module_loading.loaders.versions_parser import (
    order_versions_in_descending_order,
    get_version_constraints
)
from checkov.terraform.module_loading.module_params import ModuleParams


class RegistryLoader(ModuleLoader):
    modules_versions_cache: Dict[str, List[str]] = {}  # noqa: CCE003  # public data

    def __init__(self) -> None:
        super().__init__()
        self.module_version_url = ""
        self.best_version = ""

    def discover(self, module_params):
        module_params.REGISTRY_URL_PREFIX = os.getenv("REGISTRY_URL_PREFIX", "https://registry.terraform.io/v1/modules")
        module_params.token = os.getenv("TFC_TOKEN", "")

    def _is_matching_loader(self, module_params: ModuleParams) -> bool:

        # Since the registry loader is the first one to be checked,
        # it shouldn't process any github modules
        if module_params.module_source.startswith(("github.com", "bitbucket.org", "git::")):
            return False

        self._process_inner_registry_module(module_params)
        if os.path.exists(module_params.dest_dir):
            return True

        if module_params.module_source.startswith(TFC_HOST_NAME):
            # indicates a private registry module
            module_params.REGISTRY_URL_PREFIX = f"https://{TFC_HOST_NAME}/api/registry/v1/modules"
            module_params.module_source = module_params.module_source.replace(f"{TFC_HOST_NAME}/", "")
        else:
            # url for the public registry
            module_params.REGISTRY_URL_PREFIX = "https://registry.terraform.io/v1/modules"

        if module_params.module_source.startswith(module_params.REGISTRY_URL_PREFIX):
            # TODO: implement registry url validation using remote service discovery
            # https://www.terraform.io/internals/remote-service-discovery#remote-service-discovery
            pass
        module_params.module_version_url = "/".join((module_params.REGISTRY_URL_PREFIX, module_params.module_source, "versions"))
        if not module_params.module_version_url.startswith(module_params.REGISTRY_URL_PREFIX):
            # Local paths don't get the prefix appended
            return False

        # If versions for a module are cached, determine the best version and return True.
        # If versions are not cached, get versions, then determine the best version and return True.
        # Best version needs to be determined here for setting most accurate dest_dir.
        if module_params.module_version_url in RegistryLoader.modules_versions_cache.keys():
            module_params.best_version = self._find_best_version(module_params)
            return True
        if not self._cache_available_versions(module_params):
            return False
        module_params.best_version = self._find_best_version(module_params)

        if not module_params.inner_module:
            module_params.dest_dir = os.path.join(module_params.root_dir, module_params.external_modules_folder_name,
                                                  TFC_HOST_NAME, *module_params.module_source.split("/"),
                                                  module_params.best_version)
        if os.path.exists(module_params.dest_dir):
            return True
        # verify cache again after refresh
        if module_params.module_version_url in RegistryLoader.modules_versions_cache.keys():
            return True
        return False

    def _load_module(self, module_params: ModuleParams) -> ModuleContent:
        if os.path.exists(module_params.dest_dir):
            return ModuleContent(dir=module_params.dest_dir)

        best_version = module_params.best_version
        logging.debug(
            f"Best version for {module_params.module_source} is {best_version} based on the version constraint {module_params.version}")
        request_download_url = "/".join((module_params.REGISTRY_URL_PREFIX, module_params.module_source, best_version, "download"))
        try:
            response = requests.get(url=request_download_url, headers={"Authorization": f"Bearer {module_params.token}"})
            response.raise_for_status()
        except HTTPError as e:
            self.logger.warning(e)
            if response.status_code != HTTPStatus.OK and response.status_code != HTTPStatus.NO_CONTENT:
                return ModuleContent(dir=None)
        else:
            # https://www.terraform.io/registry/api-docs#download-source-code-for-a-specific-module-version
            module_download_url = response.headers.get('X-Terraform-Get', '')
            self.logger.debug(f"Cloning module from: X-Terraform-Get: {module_download_url}")
            if module_download_url.startswith("https://archivist.terraform.io/v1/object"):
                try:
                    registry_getter = RegistryGetter(module_download_url)
                    registry_getter.temp_dir = module_params.dest_dir
                    registry_getter.do_get()
                    return_dir = module_params.dest_dir
                except Exception as e:
                    str_e = str(e)
                    if 'File exists' not in str_e and 'already exists and is not an empty directory' not in str_e:
                        self.logger.error(f"failed to get {module_params.module_source} because of {e}")
                        return ModuleContent(dir=None, failed_url=module_params.module_source)
                if module_params.inner_module:
                    return_dir = os.path.join(module_params.dest_dir, module_params.inner_module)
                return ModuleContent(dir=return_dir)
            else:
                return ModuleContent(dir=None, next_url=response.headers.get("X-Terraform-Get", ""))

    def _find_module_path(self, module_params: ModuleParams) -> str:
        # to determine the exact path here would be almost a duplicate of the git_loader functionality
        return ""

    def _find_best_version(self, module_params: ModuleParams) -> str:
        versions_by_size = RegistryLoader.modules_versions_cache.get(module_params.module_version_url, [])
        if module_params.version == "latest":
            module_params.version = versions_by_size[0]
        version_constraints = get_version_constraints(module_params.version)
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

    def _cache_available_versions(self, module_params: ModuleParams) -> bool:
        # Get all available versions for a module in the registry and cache them.
        # Returns False on failure.
        try:
            response = requests.get(url=module_params.module_version_url, headers={"Authorization": f"Bearer {module_params.token}"})
            response.raise_for_status()
            available_versions = [
                v.get("version") for v in response.json().get("modules", [{}])[0].get("versions", {})
            ]
            RegistryLoader.modules_versions_cache[module_params.module_version_url] = order_versions_in_descending_order(
                available_versions)
            return True
        except HTTPError as e:
            self.logger.debug(e)
            return False

    def _process_inner_registry_module(self, module_params: ModuleParams) -> None:
        # Check if the source has '//' in it. If it does, it indicates a reference for an inner module.
        # Example: "terraform-aws-modules/security-group/aws//modules/http-80" =>
        #    module_source = terraform-aws-modules/security-group/aws
        #    dest_dir = modules/http-80
        module_source_components = module_params.module_source.split("//")
        if len(module_source_components) > 1:
            module_params.module_source = module_source_components[0]
            module_params.dest_dir = module_params.dest_dir.split("//")[0]
            module_params.inner_module = module_source_components[1]


loader = RegistryLoader()
