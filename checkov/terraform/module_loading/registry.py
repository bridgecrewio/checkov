import logging
import os
from typing import Optional, List

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.module_loading.content import ModuleContent


class ModuleLoaderRegistry:
    loaders: List = []      # List[ModuleLoader]

    def __init__(self, download_external_modules=False, external_modules_folder_name=DEFAULT_EXTERNAL_MODULES_DIR):
        self.logger = logging.getLogger(__name__)
        self.download_external_modules = download_external_modules
        self.external_modules_folder_name = external_modules_folder_name
        self.failed_urls_cache = set()

    def load(self, current_dir: str, source: str, source_version: Optional[str]) -> ModuleContent:
        """
Search all registered loaders for the first one which is able to load the module source type. For more
information, see `loader.ModuleLoader.load`.
        """
        local_dir = os.path.join(current_dir, self.external_modules_folder_name, source)
        inner_module = ''
        next_url = source
        last_exception = None
        while next_url:
            source = next_url
            next_url = ''
            if source in self.failed_urls_cache:
                break
            for loader in self.loaders:
                if not self.download_external_modules and loader.is_external:
                    continue
                try:
                    content = loader.load(current_dir, source, source_version, local_dir, inner_module)
                except Exception as e:
                    last_exception = e
                    continue
                if content.next_url:
                    next_url = content.next_url
                    if loader.inner_module:
                        local_dir = loader.dest_dir
                        inner_module = loader.inner_module
                    break
                if content is None:
                    continue
                elif not content.loaded():
                    if content.failed_url:
                        self.failed_urls_cache.add(content.failed_url)
                    content.cleanup()
                    continue
                else:
                    return content

        if last_exception is not None:
            raise last_exception
        return ModuleContent(None)

    def register(self, loader):
        self.loaders.append(loader)

    def clear_all_loaders(self):
        self.loaders.clear()


module_loader_registry = ModuleLoaderRegistry()
