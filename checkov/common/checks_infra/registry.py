from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, TYPE_CHECKING

import yaml

from checkov.common.checks_infra.checks_parser import GraphCheckParser
from checkov.common.graph.checks_infra.base_parser import BaseGraphCheckParser
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.runner_filter import RunnerFilter
from checkov.common.checks_infra.resources_types import resources_types

if TYPE_CHECKING:
    from checkov.common.graph.checks_infra.base_check import BaseGraphCheck

CHECKS_POSSIBLE_ENDING = {".json", ".yaml", ".yml"}

GraphSupportedIACFrameworks = [GraphSource.TERRAFORM, GraphSource.CLOUDFORMATION, GraphSource.KUBERNETES,
                               GraphSource.TERRAFORM_PLAN, GraphSource.KUSTOMIZE, GraphSource.BICEP,
                               GraphSource.GITHUB_ACTION, GraphSource.HELM, GraphSource.ANSIBLE, GraphSource.ARM]


class Registry(BaseRegistry):
    def __init__(self, checks_dir: str, parser: BaseGraphCheckParser | None = None) -> None:
        parser = parser or BaseGraphCheckParser()

        super().__init__(parser)
        self.checks: list[BaseGraphCheck] = []
        self.checks_dir = checks_dir
        self.logger = logging.getLogger(__name__)
        add_resource_code_filter_to_logger(self.logger)

    def load_checks(self) -> None:
        if self.checks:
            # checks were previously loaded
            return

        self._load_checks_from_dir(self.checks_dir, False)

    def _load_checks_from_dir(self, directory: str, external_check: bool) -> None:
        dir = os.path.expanduser(directory)
        self.logger.debug(f"Loading external checks from {dir}")
        for root, d_names, f_names in os.walk(dir):
            self.logger.debug(f"Searching through {d_names} and {f_names}")
            for file in f_names:
                file_ending = os.path.splitext(file)[1]
                if file_ending in CHECKS_POSSIBLE_ENDING:
                    with open(os.path.join(root, file), "r") as f:
                        if dir != self.checks_dir:
                            self.logger.info(f"loading {file}")

                        if file_ending == ".json":
                            check_json = json.load(f)
                        else:
                            check_yaml = yaml.safe_load(f)
                            check_json = json.loads(json.dumps(check_yaml))

                        if not isinstance(check_json, dict):
                            self.logger.error(f"Loaded data from JSON is not Dict. Skipping. Data: {check_json}.")
                            continue

                        if not self.parser.validate_check_config(file_path=f.name, raw_check=check_json):
                            # proper log messages are generated inside the method
                            continue

                        check = self.parser.parse_raw_check(
                            check_json, resources_types=self._get_resource_types(check_json),
                            check_path=f'{root}/{file}'
                        )
                        if not any(c for c in self.checks if check.id == c.id):
                            if external_check:
                                # Note the external check; used in the should_run_check logic
                                RunnerFilter.notify_external_check(check.id)
                            self.checks.append(check)

    def load_external_checks(self, dir: str) -> None:
        self._load_checks_from_dir(dir, True)

    @staticmethod
    def _get_resource_types(check_json: dict[str, dict[str, Any]]) -> list[str] | None:
        provider = check_json.get("scope", {}).get("provider", "").lower()
        return resources_types.get(provider)


_registry_instances: dict[str, Registry] = {}


def _initialize_registry(check_type: str) -> None:
    _registry_instances[check_type] = Registry(
        parser=GraphCheckParser(),
        checks_dir=f"{Path(__file__).parent.parent.parent}/{check_type}/checks/graph_checks",
    )


def get_graph_checks_registry(check_type: str) -> Registry:
    if not _registry_instances.get(check_type):
        _initialize_registry(check_type)
    return _registry_instances[check_type]


def get_all_graph_checks_registries() -> list[Registry]:
    graph_supported_iac_frameworks = [framework.value.lower() for framework in GraphSupportedIACFrameworks]
    for framework in graph_supported_iac_frameworks:
        if not _registry_instances.get(framework):
            _initialize_registry(framework)
    return list(_registry_instances[framework] for framework in graph_supported_iac_frameworks)
