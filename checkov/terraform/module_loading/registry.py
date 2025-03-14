from __future__ import annotations

import logging
import os
import hashlib
from typing import Optional, List, TYPE_CHECKING, Set, Dict

from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.module_params import ModuleParams

if TYPE_CHECKING:
    from checkov.terraform.module_loading.loader import ModuleLoader


class ModuleLoaderRegistry:
    loaders: List["ModuleLoader"] = []  # noqa: CCE003
    module_content_cache: Dict[str, Optional[ModuleContent]] = {}  # noqa: CCE003

    def __init__(
        self, download_external_modules: bool = False, external_modules_folder_name: str = DEFAULT_EXTERNAL_MODULES_DIR
    ) -> None:
        self.logger = logging.getLogger(__name__)
        add_resource_code_filter_to_logger(self.logger)
        self.download_external_modules = download_external_modules
        self.external_modules_folder_name = external_modules_folder_name
        self.failed_urls_cache: Set[str] = set()
        self.root_dir = ""  # root dir for storing external modules

    def load(
        self,
        current_dir: str,
        source: str | None,
        source_version: str | None,
        module_address: str | None = None,
        tf_managed: bool = False,
    ) -> ModuleContent | None:
        """
Search all registered loaders for the first one which is able to load the module source type. For more
information, see `loader.ModuleLoader.load`.
        """
        if source is None:
            return None

        if module_address is None:
            module_address = f'{source}:{source_version}'
        if module_address in self.module_content_cache:
            logging.debug(f'Used the cache for module {module_address}')
            return self.module_content_cache[module_address]
        else:
            logging.debug(f'Cache miss for {module_address}')

        if os.name == 'nt':
            # For windows, due to limitations in the allowed characters for path names, the hash of the source is used.
            # https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file#naming-conventions
            source_hash = hashlib.md5(source.encode())  # nosec
            local_dir = os.path.join(self.root_dir, self.external_modules_folder_name, source_hash.hexdigest())
        else:
            local_dir = os.path.join(self.root_dir, self.external_modules_folder_name, source)
        inner_module = ""
        next_url = source
        last_exception = None
        content = ModuleContent(None)
        while next_url:
            source = next_url
            next_url = ""
            if source in self.failed_urls_cache:
                break
            logging.info(f"Iterating over {len(self.loaders)} loaders")
            for loader in self.loaders:
                if not self.download_external_modules and loader.is_external:
                    continue
                try:
                    module_params = ModuleParams(
                        root_dir=self.root_dir,
                        current_dir=current_dir,
                        source=source,
                        source_version=source_version,
                        dest_dir=local_dir,
                        external_modules_folder_name=self.external_modules_folder_name,
                        inner_module=inner_module,
                        tf_managed=tf_managed,
                    )
                    logging.info(f"Attempting loading {source} via {loader.__class__} loader")
                    content = loader.load(module_params)
                    logging.info(f"Loading result of {module_address}={content.loaded()} via {loader.__class__} loader")
                except Exception as e:
                    logging.warning(f'Module {module_address} failed to load via {loader.__class__} due to: {e}')
                    last_exception = e
                    continue
                if content.next_url:
                    next_url = content.next_url
                    if module_params.inner_module:
                        local_dir = module_params.dest_dir
                        inner_module = module_params.inner_module
                    break
                if content is None:
                    continue
                elif not content.loaded():
                    if content.failed_url:
                        self.failed_urls_cache.add(content.failed_url)
                    self.module_content_cache[module_address] = ModuleContent(None)
                    continue
                else:
                    self.module_content_cache[module_address] = content
                    return content

        if last_exception is not None:
            raise last_exception

        self.module_content_cache[module_address] = content
        return content

    def register(self, loader: "ModuleLoader") -> None:
        if loader not in self.loaders:
            self.loaders.append(loader)

    def reset_module_content_cache(self) -> None:
        self.module_content_cache = {}

    def clear_all_loaders(self) -> None:
        self.loaders.clear()


module_loader_registry = ModuleLoaderRegistry()
