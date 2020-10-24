import logging
from typing import Optional, List

from checkov.terraform.module_loading.loader import ModuleContent, ModuleLoader


class ModuleLoaderRegistry:
    loaders: List[ModuleLoader] = []

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load(self, current_dir: str, source: str, source_version: Optional[str]) -> Optional[ModuleContent]:
        """
Search all registered loaders for the first one which is able to load the module source type. For more
information, see `loader.ModuleLoader.load`.
        """
        for loader in self.loaders:
            content = loader.load(current_dir, source, source_version)
            if content is not None:
                return content
        return None

    def register(self, loader: ModuleLoader):
        self.loaders.append(loader)


module_loader_registry = ModuleLoaderRegistry()
