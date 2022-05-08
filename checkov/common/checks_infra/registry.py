from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, TYPE_CHECKING

import yaml

from checkov.common.checks_infra.checks_parser import NXGraphCheckParser
from checkov.common.graph.checks_infra.base_parser import BaseGraphCheckParser
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.runner_filter import RunnerFilter
from checkov.common.checks_infra.resources_types import resources_types

if TYPE_CHECKING:
    from checkov.common.graph.checks_infra.base_check import BaseGraphCheck

CHECKS_POSSIBLE_ENDING = [".yaml", ".yml"]


class Registry(BaseRegistry):
    def __init__(self, checks_dir: str, parser: BaseGraphCheckParser = BaseGraphCheckParser()) -> None:
        super().__init__(parser)
        self.checks: list[BaseGraphCheck] = []
        self.parser = parser
        self.checks_dir = checks_dir
        self.logger = logging.getLogger(__name__)

    def load_checks(self) -> None:
        self._load_checks_from_dir(self.checks_dir, False)

    def _load_checks_from_dir(self, directory: str, external_check: bool) -> None:
        dir = os.path.expanduser(directory)
        self.logger.debug("Loading external checks from {}".format(dir))
        for root, d_names, f_names in os.walk(dir):
            self.logger.debug(f"Searching through {d_names} and {f_names}")
            for file in f_names:
                file_ending = os.path.splitext(file)[1]
                if file_ending in CHECKS_POSSIBLE_ENDING:
                    with open(os.path.join(root, file), "r") as f:
                        if dir != self.checks_dir:
                            self.logger.info(f"loading {file}")
                        check_yaml = yaml.safe_load(f)
                        check_json = json.loads(json.dumps(check_yaml))
                        if not isinstance(check_json, dict):
                            self.logger.error(f"Loaded data from JSON is not Dict. Skipping. Data: {check_json}.")
                            continue
                        check = self.parser.parse_raw_check(
                            check_json, resources_types=self._get_resource_types(check_json)
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


def get_graph_checks_registry(check_type: str) -> Registry:
    if not _registry_instances.get(check_type):
        _registry_instances[check_type] = Registry(parser=NXGraphCheckParser(),
                             checks_dir=f"{Path(__file__).parent.parent.parent}/{check_type}/checks/graph_checks")
    return _registry_instances[check_type]
