import json
import os

import yaml

from checkov.graph.checks.checks_infra.base_parser import BaseGraphCheckParser
from checkov.graph.checks.checks_infra.registry import BaseRegistry
from checkov.graph.terraform.checks.checks_infra.resources_types import resources_types

CHECKS_POSSIBLE_ENDING = [".yaml"]


class Registry(BaseRegistry):
    def __init__(self, parser=BaseGraphCheckParser()):
        super().__init__(parser)
        self.checks = []
        self.parser = parser

    def load_checks(self):
        for root, d_names, f_names in os.walk(os.getcwd()):
            for file in f_names:
                file_ending = os.path.splitext(file)[1]
                if file_ending in CHECKS_POSSIBLE_ENDING:
                    with open(file, "r") as f:
                        check_yaml = yaml.safe_load(f)
                        check_json = json.loads(json.dumps(check_yaml))
                        check = self.parser.parse_raw_check(check_json, resources_types=self._get_resource_types(check_json))

                        self.checks.append(check)

    @staticmethod
    def _get_resource_types(check_json):
        provider = check_json.get("scope", {}).get("provider", "").lower()
        return resources_types.get(provider)
