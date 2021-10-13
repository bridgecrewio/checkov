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
        self.module_source: str = ""
        self.current_dir: str = ""
        self.dest_dir: str = ""
        self.external_modules_folder_name: str = ""
        self.version = "latest"
        self.is_external = True
        self.inner_module: Optional[str] = None
        self.root_dir = ""  # root dir for storing external modules

    def load(
        self,
        root_dir: str,
        current_dir: str,
        source: str,
        source_version: Optional[str],
        dest_dir: str,
        external_modules_folder_name: str,
        inner_module: Optional[str] = None,
    ) -> ModuleContent:
        """
This function provides an opportunity for the loader to load a module's content if it chooses to do so.
There are three resulting states that can occur when calling this function:
 1) the loader can't handle the source type, in which case a ModuleContent is returned for which
    the `loaded()` method will return False.
 2) the loader can handle the source type and loading is successful, in which case a ModuleContent
    object is returned for which `loaded()` returns True and which provides the directory containing
    the module files
 3) the loader tried to load the module content but and error occurred, in which case an exception
    is raised.
        :param current_dir: Directory containing the reference to the module.
        :param source: the raw source string from the module's `source` attribute (e.g.,
                       "hashicorp/consul/aws" or "git::https://example.com/vpc.git?ref=v1.2.0")
        :param source_version: contains content from the module's `version` attribute, if provided
        :param dest_dir: where to save the downloaded module
        :return: A ModuleContent object which may or may not being loaded.
        """
        self.root_dir = root_dir

        self.module_source = source
        self.current_dir = current_dir
        self.version = str(source_version)

        self.dest_dir = dest_dir
        self.external_modules_folder_name = external_modules_folder_name
        self.inner_module = inner_module

        if not self._is_matching_loader():
            return ModuleContent(dir=None)

        module_path = self._find_module_path()
        if os.path.exists(module_path):
            return ModuleContent(dir=module_path)

        self.logger.debug(f"getting module {self.module_source} version: {self.version}")
        return self._load_module()

    @abstractmethod
    def _is_matching_loader(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def _load_module(self) -> ModuleContent:
        raise NotImplementedError()

    @abstractmethod
    def _find_module_path(self) -> str:
        raise NotImplementedError()
