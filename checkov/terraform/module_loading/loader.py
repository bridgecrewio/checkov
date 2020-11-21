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


    @abstractmethod
    def load(self, current_dir: str, source: str, source_version: Optional[str]) -> ModuleContent:
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

        :return: A ModuleContent object which may or may not being loaded.
        """
        raise NotImplementedError()
