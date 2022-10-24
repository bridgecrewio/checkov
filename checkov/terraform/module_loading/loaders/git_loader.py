import os
import re
from dataclasses import dataclass
from pathlib import Path

from checkov.common.goget.github.get_git import GitGetter
from checkov.terraform.module_loading.content import ModuleContent

from checkov.terraform.module_loading.loader import ModuleLoader
from checkov.terraform.module_loading.module_params import ModuleParams

DEFAULT_MODULE_SOURCE_PREFIX = "git::https://"


@dataclass(frozen=True)
class ModuleSource:
    protocol: str
    root_module: str
    inner_module: str
    version: str
    username: str


class GenericGitLoader(ModuleLoader):
    def __init__(self):
        super().__init__()
        self.module_source_prefix = DEFAULT_MODULE_SOURCE_PREFIX

    @property
    def module_source_prefix(self):
        return self._module_source_prefix

    @module_source_prefix.setter
    def module_source_prefix(self, prefix):
        self._module_source_prefix = prefix

    def discover(self, module_params: ModuleParams):
        module_params.vcs_base_url = os.getenv("VCS_BASE_URL", "")  # format - https://example.com
        module_params.module_source_prefix = f"git::{module_params.vcs_base_url}" if module_params.vcs_base_url else None
        module_params.username = os.getenv("VCS_USERNAME", None)
        module_params.token = os.getenv("VCS_TOKEN", None)

    def _is_matching_loader(self, module_params: ModuleParams) -> bool:
        module_source_prefix = module_params.module_source_prefix if module_params.module_source_prefix else self.module_source_prefix
        if module_params.module_source.startswith(module_source_prefix):
            source = module_params.module_source.split(DEFAULT_MODULE_SOURCE_PREFIX)[-1]
            if module_params.token and module_params.username:
                module_params.module_source = f"{DEFAULT_MODULE_SOURCE_PREFIX}{module_params.username}:{module_params.token}@{source}"
            else:
                module_params.module_source = f"{DEFAULT_MODULE_SOURCE_PREFIX}{source}"
            return True
        # https://www.terraform.io/docs/modules/sources.html#generic-git-repository
        return module_params.module_source.startswith("git::")

    def _load_module(self, module_params: ModuleParams) -> ModuleContent:
        try:
            self._process_generic_git_repo(module_params)

            module_source = module_params.module_source.replace("git::", "")
            git_getter = GitGetter(module_source, create_clone_and_result_dirs=False)
            git_getter.temp_dir = module_params.dest_dir
            git_getter.do_get()
        except Exception as e:
            str_e = str(e)
            if 'File exists' not in str_e and 'already exists and is not an empty directory' not in str_e:
                self.logger.error(f"failed to get {module_params.module_source} because of {e}")
                return ModuleContent(dir=None, failed_url=module_params.module_source)
        return_dir = module_params.dest_dir
        if module_params.inner_module:
            return_dir = os.path.join(module_params.dest_dir, module_params.inner_module)
        return ModuleContent(dir=return_dir)

    def _find_module_path(self, module_params: ModuleParams) -> str:
        module_source = self._parse_module_source(module_params)
        module_path = Path(module_params.root_dir).joinpath(
            module_params.external_modules_folder_name,
            module_source.root_module,
            module_source.version,
            module_source.inner_module,
        )

        if module_params.inner_module:
            module_path = module_path / module_params.inner_module

        return str(module_path)

    def _parse_module_source(self, module_params: ModuleParams) -> ModuleSource:
        module_source_components = module_params.module_source.split("//")

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
            username=username[1] if username and username[1] != "git@" else ""
        )

    def _process_generic_git_repo(self, module_params: ModuleParams) -> None:
        module_source = self._parse_module_source(module_params)

        if module_source.inner_module:
            module_params.dest_dir = str(
                Path(module_params.root_dir).joinpath(
                    module_params.external_modules_folder_name, module_source.root_module, module_source.version
                )
            )
            module_params.inner_module = module_source.inner_module
            module_params.module_source = f"{module_source.protocol}//{module_source.root_module}"
            if module_source.username:
                module_params.module_source = f"{module_source.protocol}//{module_source.username}{module_source.root_module}"
            if module_source.version != "HEAD":
                module_params.module_source += f"?ref={module_source.version}"
        else:
            module_params.dest_dir = str(
                Path(module_params.root_dir).joinpath(
                    module_params.external_modules_folder_name, module_source.root_module, module_source.version
                )
            )


loader = GenericGitLoader()
