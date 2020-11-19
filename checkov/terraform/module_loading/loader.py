import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.registry import module_loader_registry


# ModuleContent allows access to a directory containing module file via the `path()`
# function. Instances may be used in a `with` context to ensure temporary directories
# are removed, if applicable.


class ModuleLoader(ABC):
    def __init__(self) -> None:
        module_loader_registry.register(self)
        self.logger = logging.getLogger(__name__)
        self.module_source = None
        self.current_dir = None
        self.dest_dir = None
        self.version = 'latest'
        self.is_external = True

    def load(self, current_dir: str, source: str, source_version: Optional[str], dest_dir) -> ModuleContent:
        self.module_source = source
        self.current_dir = current_dir
        self.version = str(source_version)

        self.dest_dir = dest_dir
        if os.path.exists(self.dest_dir):
            return ModuleContent(dir=self.dest_dir)

        if not self._is_matching_loader():
            return ModuleContent(dir=None)
        self.logger.debug(f'getting module {self.module_source} version: {self.version}')
        return self._load_module()

    @abstractmethod
    def _is_matching_loader(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def _load_module(self) -> ModuleContent:
        raise NotImplementedError()
