import logging
import os
import hashlib
from typing import Optional, List, TYPE_CHECKING, Set

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.module_loading.content import ModuleContent

if TYPE_CHECKING:
    from checkov.terraform.module_loading.loader import ModuleLoader


class ModuleLoaderRegistry:
    loaders: List["ModuleLoader"] = []

    def __init__(
        self, download_external_modules: bool = False, external_modules_folder_name: str = DEFAULT_EXTERNAL_MODULES_DIR
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.download_external_modules = download_external_modules
        self.external_modules_folder_name = external_modules_folder_name
        self.failed_urls_cache: Set[str] = set()
        self.root_dir = ""  # root dir for storing external modules

    def load(self, current_dir: str, source: str, source_version: Optional[str]) -> ModuleContent:
        """
Search all registered loaders for the first one which is able to load the module source type. For more
information, see `loader.ModuleLoader.load`.
        """
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
        while next_url:
            source = next_url
            next_url = ""
            if source in self.failed_urls_cache:
                break
            for loader in self.loaders:
                if not self.download_external_modules and loader.is_external:
                    continue
                try:
                    content = loader.load(
                        root_dir=self.root_dir,
                        current_dir=current_dir,
                        source=source,
                        source_version=source_version,
                        dest_dir=local_dir,
                        external_modules_folder_name=self.external_modules_folder_name,
                        inner_module=inner_module,
                    )
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

    def register(self, loader: "ModuleLoader") -> None:
        self.loaders.append(loader)

    def clear_all_loaders(self) -> None:
        self.loaders.clear()


module_loader_registry = ModuleLoaderRegistry()
