from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import List, Callable, TYPE_CHECKING

from checkov.common.util.env_vars_config import env_vars_config
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.util.file_utils import read_file_with_any_encoding
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


def find_tf_managed_modules(path: str) -> List[ModuleDownload]:
    """
    Leverage modules.json to better inform discovery. If we have this,
    there should be no need to walk and gather modules.
    """
    modules_found: list[ModuleDownload] = []

    tf_modules_file = Path(path) / '.terraform' / 'modules' / 'modules.json'
    if not tf_modules_file.exists():
        return modules_found

    for mod in json.loads(tf_modules_file.read_bytes())['Modules']:
        if mod['Key']:
            md = ModuleDownload(path)
            md.module_name = mod['Key']
            md.module_link = mod['Dir']
            md.version = mod['Version'] if 'Version' in mod else 'latest'
            md.address = f"{mod['Source']}:{md.version}"
            md.tf_managed = True
            modules_found.append(md)
    return modules_found


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
                comment_out = re.findall(r'/\*.*?\*/', content, re.DOTALL)
                for line in content.splitlines():
                    if not curr_md:
                        if line.startswith('module'):
                            in_comment_out = [line for a in comment_out if line in a]
                            if in_comment_out:
                                # if the "module " ref in the comment out part
                                continue
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
    if not modules_to_load and env_vars_config.CHECKOV_EXPERIMENTAL_TERRAFORM_MANAGED_MODULES:
        modules_to_load = find_tf_managed_modules(path)
    if not modules_to_load:
        modules_to_load = find_modules(path)

    # To avoid duplicate work, we need to get the distinct module sources
    distinct_modules = list({m.address: m for m in modules_to_load}.values())

    downloadable_modules = [
        (module_loader_registry, m)
        for m in distinct_modules if should_download_module(m.module_link)
    ]

    if run_parallel:
        list(parallel_runner.run_function(_download_module, downloadable_modules))
    else:
        logging.info(f"Starting download of modules of length {len(downloadable_modules)}")
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
            if ml_registry.download_external_modules is not False:
                log_message = f'Failed to download module {module_download.address}'
                if ml_registry.download_external_modules is None:
                    log_message += ' (for external modules, the --download-external-modules flag is required)'
                logging.warning(log_message)
            return False
    except Exception as e:
        logging.warning(f"Unable to load module ({module_download.address}): {e}")
        return False

    return True
