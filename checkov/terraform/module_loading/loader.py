import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.module_params import ModuleParams
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

    @abstractmethod
    def discover(self, module_params: ModuleParams):
        """
            discover parameters from execution context of checkov. usually from env variable
        """
        pass

    def load(self, module_params: ModuleParams) -> ModuleContent:
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
        :param module_params: dataclass object that contains all the parameters of the module to load.
                              the data of this object can be changed according to the loader logic
        :return: A ModuleContent object which may or may not being loaded.
        """
        self.discover(module_params)
        if not self._is_matching_loader(module_params):
            return ModuleContent(dir=None)

        module_path = self._find_module_path(module_params)
        if os.path.exists(module_path):
            return ModuleContent(dir=module_path)

        self.logger.debug(f"Using {self.__class__.__name__} attempting to get module "
                          f"{module_params.module_source if '@' not in module_params.module_source else module_params.module_source.split('@')[1]} "
                          f"version: {module_params.version}")
        return self._load_module(module_params)

    @abstractmethod
    def _is_matching_loader(self, module_params: ModuleParams) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def _load_module(self, module_params: ModuleParams) -> ModuleContent:
        raise NotImplementedError()

    @abstractmethod
    def _find_module_path(self, module_params: ModuleParams) -> str:
        raise NotImplementedError()
