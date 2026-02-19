from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from checkov.common.goget.s3.get_s3 import S3Getter
from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.loader import ModuleLoader

if TYPE_CHECKING:
    from checkov.terraform.module_loading.module_params import ModuleParams

S3_MODULE_SOURCE_PREFIX = "s3::"
# Regex pattern to strip archive extensions from paths for directory naming
ARCHIVE_EXTENSION_PATTERN = re.compile(r"\.(zip|tar\.bz2|tar\.gz|tgz|tar\.xz|txz)$")


class S3Loader(ModuleLoader):
    def __init__(self) -> None:
        super().__init__()
        self.is_external = True

    def discover(self, module_params: ModuleParams) -> None:
        # No special discovery needed - boto3 handles credential resolution
        pass

    def _is_matching_loader(self, module_params: ModuleParams) -> bool:
        # https://developer.hashicorp.com/terraform/language/modules/sources#s3-bucket
        if not module_params.module_source.startswith(S3_MODULE_SOURCE_PREFIX):
            return False
        # Process inner module and dest_dir early so _find_module_path works correctly
        # for the cache check in the base class load() method
        self._process_s3_source(module_params)
        return True

    def _load_module(self, module_params: ModuleParams) -> ModuleContent:
        try:
            s3_url = module_params.module_source.replace(S3_MODULE_SOURCE_PREFIX, "", 1)

            s3_getter = S3Getter(s3_url, create_clone_and_result_dirs=False)
            s3_getter.temp_dir = module_params.dest_dir
            s3_getter.do_get()
        except Exception as e:
            str_e = str(e)
            if "File exists" not in str_e and "already exists and is not an empty directory" not in str_e:
                self.logger.warning(f"Failed to download {module_params.module_source} from S3: {e}")
                return ModuleContent(dir=None, failed_url=module_params.module_source)

        return_dir = module_params.dest_dir
        if module_params.inner_module:
            return_dir = os.path.join(module_params.dest_dir, module_params.inner_module)

        return ModuleContent(dir=return_dir)

    def _find_module_path(self, module_params: ModuleParams) -> str:
        s3_url = module_params.module_source.replace(S3_MODULE_SOURCE_PREFIX, "", 1)
        # Remove inner module part if present (split on // but preserve the protocol //)
        s3_url = self._strip_inner_module(s3_url)

        parsed = urlparse(s3_url)
        # Use the URL path (bucket/key) as the local directory structure
        url_path = parsed.netloc + parsed.path
        # Remove archive extension for the directory name
        url_path = ARCHIVE_EXTENSION_PATTERN.sub("", url_path)

        if os.name == "nt":
            url_hash = hashlib.md5(url_path.encode()).hexdigest()  # nosec
            module_path = Path(module_params.root_dir).joinpath(
                module_params.external_modules_folder_name,
                url_hash,
            )
        else:
            module_path = Path(module_params.root_dir).joinpath(
                module_params.external_modules_folder_name,
                url_path,
            )

        if module_params.inner_module:
            module_path = module_path / module_params.inner_module

        return str(module_path)

    def _process_s3_source(self, module_params: ModuleParams) -> None:
        """Process the S3 source URL, handling inner module references via '//'."""
        # Strip the s3:: prefix for URL processing
        raw_url = module_params.module_source.replace(S3_MODULE_SOURCE_PREFIX, "", 1)

        # Check for inner module reference (e.g., s3::https://...module.zip//modules/vpc)
        # We need to be careful not to split on the protocol's //
        parsed = urlparse(raw_url)
        path_parts = parsed.path.split("//")
        if len(path_parts) > 1:
            # Inner module found after //
            base_path = path_parts[0]
            inner_module = "//".join(path_parts[1:])
            module_params.inner_module = inner_module
            base_url = f"{parsed.scheme}://{parsed.netloc}{base_path}"
            module_params.module_source = S3_MODULE_SOURCE_PREFIX + base_url

        # Set the dest_dir based on the S3 URL
        s3_url = module_params.module_source.replace(S3_MODULE_SOURCE_PREFIX, "", 1)
        parsed = urlparse(s3_url)
        url_path = parsed.netloc + parsed.path
        # Remove archive extension for the directory name
        url_path = ARCHIVE_EXTENSION_PATTERN.sub("", url_path)

        if os.name == "nt":
            # On Windows, use hash to avoid invalid path characters (e.g., ':' from URLs)
            url_hash = hashlib.md5(url_path.encode()).hexdigest()  # nosec
            module_params.dest_dir = str(
                Path(module_params.root_dir).joinpath(
                    module_params.external_modules_folder_name,
                    url_hash,
                )
            )
        else:
            module_params.dest_dir = str(
                Path(module_params.root_dir).joinpath(
                    module_params.external_modules_folder_name,
                    url_path,
                )
            )

    @staticmethod
    def _strip_inner_module(url: str) -> str:
        """Remove the inner module path (after //) from an S3 URL, preserving the protocol://."""
        parsed = urlparse(url)
        path_parts = parsed.path.split("//")
        base_path = path_parts[0]
        return f"{parsed.scheme}://{parsed.netloc}{base_path}"


loader = S3Loader()
