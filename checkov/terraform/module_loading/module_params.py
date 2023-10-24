from dataclasses import dataclass
from typing import Optional


@dataclass
class ModuleParams:
    def __init__(
        self,
        root_dir: str,
        current_dir: str,
        source: str,
        source_version: Optional[str],
        dest_dir: str,
        external_modules_folder_name: str,
        inner_module: Optional[str] = None,
        tf_managed: bool = False,
    ):
        self.root_dir: str = root_dir
        self.current_dir: str = current_dir
        self.module_source: str = source
        self.version: Optional[str] = source_version
        self.dest_dir: str = dest_dir
        self.external_modules_folder_name: str = external_modules_folder_name
        self.inner_module: Optional[str] = inner_module
        self.tf_managed = tf_managed

        self.token: Optional[str] = None
        self.username: Optional[str] = None
        self.vcs_base_url: Optional[str] = None
        self.module_source_prefix: Optional[str] = None
        self.best_version: Optional[str] = None

        # terraform cloud / enterprise specific params
        self.tf_host_name: Optional[str] = None
        self.tf_modules_endpoint: Optional[str] = None
        self.tf_modules_versions_endpoint: Optional[str] = None
