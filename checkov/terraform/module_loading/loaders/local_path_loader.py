import os
from typing import Optional

from checkov.terraform.module_loading.loader import ModuleLoader
from checkov.terraform.module_loading.content import ModuleContent


class LocalPathLoader(ModuleLoader):
    def load(self, current_dir: str, source: str, source_version: Optional[str]) -> ModuleContent:
        # Local path references start with "./" or "../"
        if not source.startswith("./") and not source.startswith("../"):
            return ModuleContent(None)

        module_path = os.path.normpath(os.path.join(current_dir, source))
        if not os.path.exists(module_path):
            raise FileNotFoundError(module_path)

        return ModuleContent(module_path)


loader = LocalPathLoader()
