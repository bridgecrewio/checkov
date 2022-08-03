import os
import platform
import re
import logging

from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.loader import ModuleLoader
from checkov.terraform.module_loading.module_params import ModuleParams


class LocalPathLoader(ModuleLoader):
    def __init__(self) -> None:
        super().__init__()
        self.is_external = False

    def discover(self, module_params: ModuleParams):
        pass

    def _is_matching_loader(self, module_params: ModuleParams) -> bool:
        if (
            module_params.module_source.startswith("./")
            or module_params.module_source.startswith("../")
            or module_params.module_source.startswith(module_params.current_dir)
            or module_params.module_source.startswith("/")
        ):
            return True

        if platform.system() == "Windows":
            logging.debug("Platform: Windows")
            if re.match(re.compile("[a-zA-Z]:\\\\"), module_params.module_source):
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
