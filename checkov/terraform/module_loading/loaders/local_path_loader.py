import os
import platform
import re
import logging

from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.loader import ModuleLoader


class LocalPathLoader(ModuleLoader):
    def __init__(self) -> None:
        super().__init__()
        self.discover()
        self.is_external = False

    def discover(self):
        pass

    def _is_matching_loader(self) -> bool:
        if (
            self.module_source.startswith("./")
            or self.module_source.startswith("../")
            or self.module_source.startswith(self.current_dir)
            or self.module_source.startswith("/")
        ):
            return True

        if platform.system() == "Windows":
            logging.debug("Platform: Windows")
            if re.match(re.compile("[a-zA-Z]:\\\\"), self.module_source):
                return True

        return False

    def _load_module(self) -> ModuleContent:
        module_path = os.path.normpath(os.path.join(self.current_dir, self.module_source))
        if self.module_source.startswith(self.current_dir):
            module_path = self.module_source
        if not os.path.exists(module_path):
            raise FileNotFoundError(module_path)

        return ModuleContent(module_path)

    def _find_module_path(self) -> str:
        # to determine the exact path here would mimic _load_module()
        return ""


loader = LocalPathLoader()
