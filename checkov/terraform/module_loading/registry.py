import logging
from typing import Optional, List

from checkov.terraform.module_loading.content import ModuleContent


class ModuleLoaderRegistry:
    loaders: List = []      # List[ModuleLoader]

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load(self, current_dir: str, source: str, source_version: Optional[str]) -> ModuleContent:
        """
Search all registered loaders for the first one which is able to load the module source type. For more
information, see `loader.ModuleLoader.load`.
        """
        last_exception = None
        for loader in self.loaders:
            try:
                content = loader.load(current_dir, source, source_version)
            except Exception as e:
                last_exception = e
                continue

            if content is None:
                continue
            elif not content.loaded():
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
