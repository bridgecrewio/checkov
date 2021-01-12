import os

from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.loader import ModuleLoader


class LocalPathLoader(ModuleLoader):
    def __init__(self) -> None:
        super().__init__()
        self.is_external = False

    def _is_matching_loader(self) -> bool:
        return self.module_source.startswith("./") or self.module_source.startswith("../") \
               or self.module_source.startswith(self.current_dir) or self.module_source.startswith('/')

    def _load_module(self) -> ModuleContent:
        module_path = os.path.normpath(os.path.join(self.current_dir, self.module_source))
        if self.module_source.startswith(self.current_dir):
            module_path = self.module_source
        if not os.path.exists(module_path):
            raise FileNotFoundError(module_path)

        return ModuleContent(module_path)


loader = LocalPathLoader()
