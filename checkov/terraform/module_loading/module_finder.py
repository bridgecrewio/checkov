from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import List, Callable, TYPE_CHECKING

from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.util.file_utils import read_file_with_any_encoding
from checkov.common.util.type_forcers import convert_str_to_bool
from checkov.terraform.module_loading.registry import module_loader_registry

if TYPE_CHECKING:
    from checkov.terraform.module_loading.registry import ModuleLoaderRegistry

MODULE_NAME_PATTERN = re.compile(r'[^#]*\bmodule\s*"(?P<name>.*)"')
MODULE_SOURCE_PATTERN = re.compile(r'[^#]*\bsource\s*=\s*"(?P<link>.*)"')
MODULE_VERSION_PATTERN = re.compile(r'[^#]*\bversion\s*=\s*"(?P<operator>=|!=|>=|>|<=|<|~>\s*)?(?P<version>[\d.]+-?\w*)"')


class ModuleDownload:
    def __init__(self, source_dir: str) -> None:
        self.source_dir = source_dir
        self.address: str | None = None
        self.module_name: str | None = None
        self.module_link: str | None = None
        self.tf_managed = False
        self.version: str | None = None

    def __str__(self) -> str:
        return f"{self.source_dir} -> {self.module_link} ({self.version})"


def find_modules(path: str) -> List[ModuleDownload]:
    modules_found: list[ModuleDownload] = []

    for root, _, full_file_names in os.walk(path):
        for file_name in full_file_names:
            if not file_name.endswith('.tf'):
                continue
            if root.startswith(os.path.join(path, ".terraform", "modules")):
                # don't scan the modules folder used by Terraform
                continue

            try:
                content = read_file_with_any_encoding(file_path=os.path.join(path, root, file_name))
                if "module " not in content:
                    # if there is no "module " ref in the whole file, then no need to search line by line
                    continue

                curr_md = None
                for line in content.splitlines():
                    if not curr_md:
                        if line.startswith('module'):
                            curr_md = ModuleDownload(os.path.dirname(os.path.join(root, file_name)))

                            # also extract the name for easier mapping against the TF modules.json file
                            match = re.match(MODULE_NAME_PATTERN, line)
                            if match:
                                curr_md.module_name = match.group("name")

                            continue
                    else:
                        if line.startswith('}'):
                            if curr_md.module_link is None:
                                logging.warning(f'A module at {curr_md.source_dir} had no source, skipping')
                            else:
                                curr_md.address = f"{curr_md.module_link}:{curr_md.version}"
                                modules_found.append(curr_md)
                            curr_md = None
                            continue

                        if "source" in line:
                            match = re.match(MODULE_SOURCE_PATTERN, line)
                            if match:
                                curr_md.module_link = match.group('link')
                                continue

                        if "version" in line:
                            match = re.match(MODULE_VERSION_PATTERN, line)
                            if match:
                                curr_md.version = f"{match.group('operator')}{match.group('version')}" if match.group('operator') else match.group('version')
            except (UnicodeDecodeError, FileNotFoundError) as e:
                logging.warning(f"Skipping {os.path.join(path, root, file_name)} because of {e}")
                continue

    return modules_found


def should_download(path: str | None) -> bool:

    return path is not None and not (path.startswith('./') or path.startswith('../') or path.startswith('/'))


def load_tf_modules(
    path: str,
    should_download_module: Callable[[str | None], bool] = should_download,
    run_parallel: bool = False,
    modules_to_load: List[ModuleDownload] | None = None,
    stop_on_failure: bool = False
) -> None:
    module_loader_registry.root_dir = path
    if not modules_to_load:
        modules_to_load = find_modules(path)

    # To avoid duplicate work, we need to get the distinct module sources
    distinct_modules = list({m.address: m for m in modules_to_load}.values())

    replaced_modules = replace_terraform_managed_modules(path=path, found_modules=distinct_modules)

    downloadable_modules = [
        (module_loader_registry, m)
        for m in replaced_modules if should_download_module(m.module_link)
    ]

    if run_parallel:
        list(parallel_runner.run_function(_download_module, downloadable_modules))
    else:
        logging.info(f"Starting download of modules of length {len(replaced_modules)}")
        for m in downloadable_modules:
            success = _download_module(*m)
            if not success and stop_on_failure:
                logging.info(f"Stopping downloading of modules due to failed attempt on {m[1].address}")
                break


def _download_module(ml_registry: ModuleLoaderRegistry, module_download: ModuleDownload) -> bool:
    logging.info(f'Downloading module {module_download.address}')
    try:
        content = ml_registry.load(
            current_dir=module_download.source_dir,
            source=module_download.module_link,
            source_version="latest" if not module_download.version else module_download.version,
            module_address=module_download.address,
            tf_managed=module_download.tf_managed,
        )
        if content is None or not content.loaded():
            log_message = f'Failed to download module {module_download.address}'
            if not ml_registry.download_external_modules:
                log_message += ' (for external modules, the --download-external-modules flag is required)'
            logging.warning(log_message)
            return False
    except Exception as e:
        logging.warning(f"Unable to load module ({module_download.address}): {e}")
        return False

    return True


def replace_terraform_managed_modules(path: str, found_modules: list[ModuleDownload]) -> list[ModuleDownload]:
    """Replaces modules by Terraform managed ones to prevent addtional downloading

    It can't handle nested modules yet, ex.
    {
      "Key": "parent_module.child_module",
      "Source": "./child_module",
      "Dir": "parent_module/child_module"
    }
    """

    if not convert_str_to_bool(os.getenv("CHECKOV_EXPERIMENTAL_TERRAFORM_MANAGED_MODULES", False)):
        return found_modules

    # file used by Terraform internally to map modules to the downloaded path
    tf_modules_file = Path(path) / ".terraform/modules/modules.json"
    if not tf_modules_file.exists():
        return found_modules

    # create Key (module name) to module detail map for faster querying
    tf_modules = {
        module["Key"]: module
        for module in json.loads(tf_modules_file.read_bytes())["Modules"]
    }

    replaced_modules: list[ModuleDownload] = []
    for module in found_modules:
        if module.module_name in tf_modules:
            tf_module = tf_modules[module.module_name]

            module_new = ModuleDownload(source_dir=path)
            # if version is 'None' then set it to latest in the address, so it can be mapped properly later on
            module_new.address = f"{module.module_link}:latest" if module.version is None else module.address
            module_new.module_link = tf_module["Dir"]
            module_new.module_name = module.module_name
            module_new.tf_managed = True
            module_new.version = module.version

            replaced_modules.append(module_new)
        else:
            replaced_modules.append(module)

    return replaced_modules
