from __future__ import annotations

import os
from http import HTTPStatus
from typing import List, Dict, TYPE_CHECKING

import requests
from requests.exceptions import HTTPError
from urllib.parse import urljoin
from urllib.parse import urlparse

from checkov.common.models.consts import TFC_HOST_NAME
from checkov.common.goget.registry.get_registry import RegistryGetter
from checkov.common.util.http_utils import DEFAULT_TIMEOUT
from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.loader import ModuleLoader
from checkov.terraform.module_loading.loaders.versions_parser import (
    order_versions_in_descending_order,
    get_version_constraints
)
from checkov.common.proxy.proxy_client import call_http_request_with_proxy

if TYPE_CHECKING:
    from checkov.terraform.module_loading.module_params import ModuleParams

# https://developer.hashicorp.com/terraform/language/modules/sources#fetching-archives-over-http
MODULE_ARCHIVE_EXTENSIONS = ["zip", "tar.bz2", "tar.gz", "tgz", "tar.xz", "txz"]


class RegistryLoader(ModuleLoader):
    modules_versions_cache: Dict[str, List[str]] = {}  # noqa: CCE003  # public data

    def __init__(self) -> None:
        super().__init__()

    def discover(self, module_params: ModuleParams) -> None:
        module_params.tf_host_name = os.getenv("TF_HOST_NAME", TFC_HOST_NAME)
        module_params.token = os.getenv("TF_REGISTRY_TOKEN", "")
        tfc_token = os.getenv("TFC_TOKEN")
        if tfc_token:
            self.logger.warn("Environment variable TFC_TOKEN will be deprecated in the future. Please use TF_REGISTRY_TOKEN instead.")
            module_params.token = tfc_token

    def _is_matching_loader(self, module_params: ModuleParams) -> bool:
        # https://developer.hashicorp.com/terraform/language/modules/sources#github
        if module_params.module_source.startswith(("/", "github.com", "bitbucket.org", "git::", "git@github.com")):
            return False
        self._process_inner_registry_module(module_params)
        # determine tf api endpoints
        self._determine_tf_api_endpoints(module_params)
        # If versions for a module are cached, determine the best version and return True.
        # If versions are not cached, get versions, then determine the best version and return True.
        # Best version needs to be determined here for setting most accurate dest_dir.
        if module_params.tf_modules_versions_endpoint in RegistryLoader.modules_versions_cache.keys():
            module_params.best_version = self._find_best_version(module_params)
            return True
        if not self._cache_available_versions(module_params):
            return False
        module_params.best_version = self._find_best_version(module_params)
        if not module_params.inner_module and module_params.tf_host_name:
            module_params.dest_dir = os.path.join(module_params.root_dir, module_params.external_modules_folder_name,
                                                  module_params.tf_host_name, *module_params.module_source.split("/"),
                                                  module_params.best_version)
        if os.path.exists(module_params.dest_dir):
            return True
        # verify cache again after refresh
        if module_params.tf_modules_versions_endpoint in RegistryLoader.modules_versions_cache.keys():
            return True
        return False

    def _load_module(self, module_params: ModuleParams) -> ModuleContent:
        if module_params.best_version:
            best_version = module_params.best_version
        else:
            if self._cache_available_versions(module_params):
                module_params.best_version = self._find_best_version(module_params)
        if os.path.exists(module_params.dest_dir):
            return ModuleContent(dir=module_params.dest_dir)
        elif not module_params.tf_modules_endpoint:
            return ModuleContent(dir=None)

        request_download_url = urljoin(module_params.tf_modules_endpoint, "/".join((module_params.module_source, best_version, "download")))
        self.logger.debug(f"Best version for {module_params.module_source} is {best_version} based on the version constraint {module_params.version}.")
        self.logger.debug(f"Module download url: {request_download_url} and proxy: {os.getenv('PROXY_URL')}")
        try:
            request = requests.Request(
                method='GET',
                url=request_download_url,
                headers={"Authorization": f"Bearer {module_params.token}"} if module_params.token else None
            )
            if os.getenv('PROXY_URL'):
                self.logger.info(f'Sending request to {request.url} through proxy')
                response = call_http_request_with_proxy(request)
            else:
                session = requests.Session()
                prepared_request = session.prepare_request(request)
                response = session.send(prepared_request, timeout=DEFAULT_TIMEOUT)

            response.raise_for_status()
        except HTTPError as e:
            self.logger.warning(e)
            if response.status_code != HTTPStatus.OK and response.status_code != HTTPStatus.NO_CONTENT:
                return ModuleContent(dir=None)
        # https://www.terraform.io/registry/api-docs#download-source-code-for-a-specific-module-version
        module_download_url = response.headers.get('X-Terraform-Get', '')
        self.logger.debug(f"X-Terraform-Get: {module_download_url}")
        module_download_url = self._normalize_module_download_url(module_params, module_download_url)
        self.logger.debug(f"Cloning module from normalized url {module_download_url}")
        archive_extension = self._get_archive_extension(module_download_url)
        if archive_extension:
            try:
                registry_getter = RegistryGetter(module_download_url, archive_extension)
                registry_getter.temp_dir = module_params.dest_dir
                registry_getter.do_get()
                return_dir = module_params.dest_dir
            except Exception as e:
                str_e = str(e)
                if 'File exists' not in str_e and 'already exists and is not an empty directory' not in str_e:
                    self.logger.error(f"failed to get {module_params.module_source} in registry loader because of {e}")
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
        versions_by_size = RegistryLoader.modules_versions_cache.get(module_params.tf_modules_versions_endpoint, [])  # type:ignore[arg-type]  # argument can be None
        if module_params.version == "latest":
            module_params.version = versions_by_size[0]
        elif module_params.version is None:
            return "latest"

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
        if not module_params.tf_modules_versions_endpoint:
            return False

        try:
            request = requests.Request(
                method='GET',
                headers={"Authorization": f"Bearer {module_params.token}"} if module_params.token else None,
                url=module_params.tf_modules_versions_endpoint
            )
            if os.getenv('PROXY_URL'):
                self.logger.info(f'Sending request to {request.url} through proxy')
                response = call_http_request_with_proxy(request)
            else:
                session = requests.Session()
                prepared_request = session.prepare_request(request)
                response = session.send(prepared_request, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            available_versions = [
                v.get("version") for v in response.json().get("modules", [{}])[0].get("versions", {})
            ]
            RegistryLoader.modules_versions_cache[module_params.tf_modules_versions_endpoint] = order_versions_in_descending_order(
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

    def _determine_tf_api_endpoints(self, module_params: ModuleParams) -> None:
        """
        Determines terraform registry endpoints - tf_host_name, tf_modules_endpoint, tf_modules_versions_endpoint
        """
        if module_params.tf_host_name and module_params.module_source.startswith(module_params.tf_host_name):
            # check if module source supports native Terraform services
            # https://www.terraform.io/internals/remote-service-discovery#remote-service-discovery
            module_params.module_source = module_params.module_source.replace(f"{module_params.tf_host_name}/", "")
            try:
                request = requests.Request(
                    method='GET',
                    url=f"https://{module_params.tf_host_name}/.well-known/terraform.json"
                )
                if os.getenv('PROXY_URL'):
                    self.logger.info(f'Sending request to {request.url} through proxy')
                    response = call_http_request_with_proxy(request)
                else:
                    session = requests.Session()
                    prepared_request = session.prepare_request(request)
                    response = session.send(prepared_request, timeout=DEFAULT_TIMEOUT)
                response.raise_for_status()
            except HTTPError as e:
                self.logger.debug(e)
                if response.status_code != HTTPStatus.OK and response.status_code != HTTPStatus.NO_CONTENT:
                    return None

            self.logger.debug(f"Service discovery response: {response.json()}")
            module_params.tf_modules_endpoint = self._normalize_module_download_url(module_params, response.json().get('modules.v1'))
        else:
            # use terraform cloud host name and url for the public registry
            module_params.tf_host_name = TFC_HOST_NAME
            module_params.tf_modules_endpoint = "https://registry.terraform.io/v1/modules/"

        # assume module_params.tf_modules_endpoint ends with a slash as per https://developer.hashicorp.com/terraform/internals/module-registry-protocol#service-discovery
        module_params.tf_modules_versions_endpoint = urljoin(module_params.tf_modules_endpoint, "/".join((module_params.module_source, "versions")))

    def _normalize_module_download_url(self, module_params: ModuleParams, module_download_url: str) -> str:
        if not urlparse(module_download_url).netloc:
            module_download_url = f"https://{module_params.tf_host_name}{module_download_url}"
        return module_download_url

    @staticmethod
    def _get_archive_extension(module_download_url: str) -> str | None:
        module_download_path = urlparse(module_download_url).path
        for extension in MODULE_ARCHIVE_EXTENSIONS:
            if module_download_path.endswith(extension):
                return extension
        query_params_str = urlparse(module_download_url).query
        if query_params_str:
            query_params = query_params_str.split("&")
            for query_param in query_params:
                if query_param.startswith("archive="):
                    return query_params_str.split("=")[1]
        return None


loader = RegistryLoader()
