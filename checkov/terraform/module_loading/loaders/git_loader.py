import os
import re
from dataclasses import dataclass
from pathlib import Path

from checkov.common.goget.github.get_git import GitGetter
from checkov.terraform.module_loading.content import ModuleContent

from checkov.terraform.module_loading.loader import ModuleLoader


@dataclass(frozen=True)
class ModuleSource:
    protocol: str
    root_module: str
    inner_module: str
    version: str


class GenericGitLoader(ModuleLoader):
    def _is_matching_loader(self) -> bool:
        # https://www.terraform.io/docs/modules/sources.html#generic-git-repository
        return self.module_source.startswith("git::")

    def _load_module(self) -> ModuleContent:
        try:
            self._process_generic_git_repo()

            module_source = self.module_source.replace("git::", "")
            git_getter = GitGetter(module_source, create_clone_and_result_dirs=False)
            git_getter.temp_dir = self.dest_dir
            git_getter.do_get()
        except Exception as e:
            str_e = str(e)
            if 'File exists' not in str_e and 'already exists and is not an empty directory' not in str_e:
                self.logger.error(f"failed to get {self.module_source} because of {e}")
                return ModuleContent(dir=None, failed_url=self.module_source)
        return_dir = self.dest_dir
        if self.inner_module:
            return_dir = os.path.join(self.dest_dir, self.inner_module)
        return ModuleContent(dir=return_dir)

    def _find_module_path(self) -> str:
        module_source = self._parse_module_source()
        module_path = Path(self.root_dir).joinpath(
            self.external_modules_folder_name,
            module_source.root_module,
            module_source.version,
            module_source.inner_module,
        )

        if self.inner_module:
            module_path = module_path / self.inner_module

        return str(module_path)

    def _parse_module_source(self) -> ModuleSource:
        module_source_components = self.module_source.split("//")

        if "?ref=" in module_source_components[-1]:
            module_version_components = module_source_components[-1].rsplit("?ref=", maxsplit=1)
            module_source_components[-1] = module_version_components[0]
            version = module_version_components[1]
        else:
            version = "HEAD"

        if len(module_source_components) < 3:
            root_module = module_source_components[-1]
            inner_module = ""
        elif len(module_source_components) == 3:
            root_module = module_source_components[1]
            inner_module = module_source_components[2]
        else:
            raise Exception("invalid git url")

        username = re.match(re.compile(r"^(.*?@).*"), root_module)
        if username and username[1] != "git@":
            root_module = root_module.replace(username[1], "")

        if root_module.endswith(".git"):
            root_module = root_module[:-4]

        return ModuleSource(
            protocol=module_source_components[0], root_module=root_module, inner_module=inner_module, version=version,
        )

    def _process_generic_git_repo(self) -> None:
        module_source = self._parse_module_source()

        if module_source.inner_module:
            self.dest_dir = str(
                Path(self.root_dir).joinpath(
                    self.external_modules_folder_name, module_source.root_module, module_source.version
                )
            )
            self.inner_module = module_source.inner_module
            self.module_source = f"{module_source.protocol}//{module_source.root_module}"
            if module_source.version != "HEAD":
                self.module_source += f"?ref={module_source.version}"
        else:
            self.dest_dir = str(
                Path(self.root_dir).joinpath(
                    self.external_modules_folder_name, module_source.root_module, module_source.version
                )
            )


loader = GenericGitLoader()
