import logging
import os

import yaml

from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks_infra.checks_parser import NXGraphCheckParser


class YamlRegistry(BaseRegistry):
    def __init__(self):
        super().__init__(parser=NXGraphCheckParser())
        self.json_checks = []
        self.logger = logging.getLogger(__name__)

    def load_checks(self):
        for check_json in self.json_checks:
            check = self.parser.parse_raw_check(check_json)
            self.checks.append(check)

    def load_external_checks(self, raw_directory: str, runner_filter: RunnerFilter):
        BaseCheckRegistry.__loading_external_checks = True
        directory = os.path.expanduser(raw_directory)

        with os.scandir(directory) as directory_content:
            for entry in directory_content:
                if entry.name.endswith('yaml') or entry.name.endswith('yml'):
                    with open(entry.path) as f:
                        res = yaml.safe_load(f)
                    check = self.parser.parse_raw_check(res)
                    if all(check.id != c.id for c in self.checks):
                        self.checks.append(check)
        BaseCheckRegistry.__loading_external_checks = False
        return

    @staticmethod
    def _process_check_result(results, processed_results, result):
        for result_entity in results:
            processed_results.append({'result': result, 'entity': result_entity})
        return processed_results


yaml_registry = YamlRegistry()
