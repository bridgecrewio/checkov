from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from checkov.ansible.graph_builder.graph_components.resource_types import ResourceType
from checkov.common.parsers.yaml.parser import parse
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.file_utils import read_file_with_any_encoding
from checkov.common.util.suppression import collect_suppressions_for_context

TASK_NAME_PATTERN = re.compile(r"^\s*-\s+name:\s+", re.MULTILINE)

# https://docs.ansible.com/ansible/latest/reference_appendices/playbooks_keywords.html#task
TASK_RESERVED_KEYWORDS = {
    "action",
    "any_errors_fatal",
    "args",
    "async",
    "become",
    "become_exe",
    "become_flags",
    "become_method",
    "become_user",
    "changed_when",
    "check_mode",
    "collections",
    "connection",
    "debugger",
    "delay",
    "delegate_facts",
    "delegate_to",
    "diff",
    "environment",
    "failed_when",
    "ignore_errors",
    "ignore_unreachable",
    "local_action",
    "loop",
    "loop_control",
    "module_defaults",
    "name",
    "no_log",
    "notify",
    "poll",
    "port",
    "register",
    "remote_user",
    "retries",
    "run_once",
    "tags",
    "throttle",
    "timeout",
    "until",
    "vars",
    "when",
}

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)


def get_scannable_file_paths(root_folder: str | Path) -> set[Path]:
    """Finds yaml files"""

    file_paths: set[Path] = set()

    if root_folder:
        root_path = root_folder if isinstance(root_folder, Path) else Path(root_folder)
        file_paths = {file_path for file_path in root_path.rglob("*.[y][am]*[l]") if file_path.is_file()}

    return file_paths


def get_relevant_file_content(file_path: str | Path) -> str | None:
    if not str(file_path).endswith((".yaml", ".yml")):
        return None

    content = read_file_with_any_encoding(file_path=file_path)
    if "name:" not in content:
        # the following regex will search more precisely, but no need to further process
        return None

    match_task_name = re.search(TASK_NAME_PATTERN, content)
    if match_task_name:
        # there are more files, which belong to an ansible playbook,
        # but we are currently only interested in 'tasks'
        return content

    return None


def parse_file(
    f: str | Path, file_content: str | None = None
) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
    file_content = get_relevant_file_content(file_path=f)
    if file_content:
        content = parse(filename=str(f), file_content=file_content)
        return content

    return None


def generate_task_name(task: dict[str, Any], prefix: str = "") -> str | None:
    # grab the task name at the beginning before trying to find the actual module name
    task_name = task.get("name") or "unknown"

    for name in task:
        if name in TASK_RESERVED_KEYWORDS:
            continue

        if prefix:
            # if the task is found in a block, then prefix the module name with 'block'
            name = f"{prefix}{name}"

        return f"{ResourceType.TASKS}.{name}.{task_name}"

    return None


def build_definitions_context(
    definitions: dict[str, dict[str, Any] | list[dict[str, Any]]],
    definitions_raw: dict[str, list[tuple[int, str]]],
) -> dict[str, dict[str, Any]]:
    definitions_context: dict[str, dict[str, Any]] = {}

    for file_path, definition in definitions.items():
        file_path_context: dict[str, Any] = {}
        definition_raw = definitions_raw[file_path]

        if not isinstance(definition, list):
            logger.info(f"File {file_path} has the wrong type {type(definition)}")
            continue

        for code_block in definition:
            if ResourceType.TASKS in code_block:
                for task in code_block[ResourceType.TASKS]:
                    _process_blocks(definition_raw=definition_raw, file_path_context=file_path_context, task=task)
            else:
                _process_blocks(definition_raw=definition_raw, file_path_context=file_path_context, task=code_block)

        definitions_context[file_path] = file_path_context

    return definitions_context


def _process_blocks(
    definition_raw: list[tuple[int, str]],
    file_path_context: dict[str, Any],
    task: Any,
    prefix: str = "",
) -> None:
    """Checks for possible block usage"""

    if not task or not isinstance(task, dict):
        return

    if ResourceType.BLOCK in task and isinstance(task[ResourceType.BLOCK], list):
        prefix += f"{ResourceType.BLOCK}."  # with each nested level an extra block prefix is added
        block_name = f"{prefix}.{task.get('name') or 'unknown'}"
        resource_context = _create_resource_context(definition_raw=definition_raw, resource=task)
        file_path_context[block_name] = resource_context

        for block_task in task[ResourceType.BLOCK]:
            _process_blocks(
                definition_raw=definition_raw, file_path_context=file_path_context, task=block_task, prefix=prefix
            )
    else:
        resource_context = _create_resource_context(definition_raw=definition_raw, resource=task)
        task_name = generate_task_name(task=task, prefix=prefix)
        if task_name:
            file_path_context[task_name] = resource_context


def _create_resource_context(definition_raw: list[tuple[int, str]], resource: dict[str, Any]) -> dict[str, Any]:
    """Creates the resource context block"""

    start_line = resource[START_LINE]
    end_line = resource[END_LINE]
    code_lines = definition_raw[start_line - 1 : end_line - 1]  # lines start with index 0
    skipped_checks = collect_suppressions_for_context(code_lines=code_lines)

    return {
        "start_line": start_line,
        "end_line": end_line - 1,
        "code_lines": code_lines,
        "skipped_checks": skipped_checks,
    }
