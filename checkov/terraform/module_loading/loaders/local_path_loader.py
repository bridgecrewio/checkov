from __future__ import annotations

import os
import platform
import re
import logging
from typing import TYPE_CHECKING

from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.loader import ModuleLoader

if TYPE_CHECKING:
    from checkov.terraform.module_loading.module_params import ModuleParams

WINDOWS_MODULE_SOURCE_PATH_PATTERN = re.compile("[a-zA-Z]:\\\\")


class LocalPathLoader(ModuleLoader):
    def __init__(self) -> None:
        super().__init__()
        self.is_external = False

    def discover(self, module_params: ModuleParams) -> None:
        pass

    def _is_matching_loader(self, module_params: ModuleParams) -> bool:
        if module_params.tf_managed:
            # Terraform managed modules are already downloaded and can be handled as local modules
            return True

        if module_params.module_source.startswith(("./", "../", module_params.current_dir, "/")):
            return True

        if platform.system() == "Windows":
            logging.debug("Platform: Windows")
            if re.match(WINDOWS_MODULE_SOURCE_PATH_PATTERN, module_params.module_source):
                return True

        return False

    def _load_module(self, module_params: ModuleParams) -> ModuleContent:
        module_path = os.path.normpath(os.path.join(module_params.current_dir, module_params.module_source))
        if module_params.module_source.startswith(module_params.current_dir):
            module_path = module_params.module_source
        if not os.path.exists(module_path):
            raise FileNotFoundError(module_path)

        return ModuleContent(module_path)

    def _find_module_path(self, module_params: ModuleParams) -> str:
        # to determine the exact path here would mimic _load_module()
        return ""


loader = LocalPathLoader()
