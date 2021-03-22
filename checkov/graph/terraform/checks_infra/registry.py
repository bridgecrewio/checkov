import json
import logging
import os
from typing import Optional, List

import yaml

from checkov.graph.checks.checks_infra.base_parser import BaseGraphCheckParser
from checkov.graph.checks.checks_infra.registry import BaseRegistry
from checkov.graph.terraform.checks_infra.resources_types import resources_types

CHECKS_POSSIBLE_ENDING = [".yaml", ".yml"]


class Registry(BaseRegistry):
    def __init__(self, parser=BaseGraphCheckParser(), checks_dir=None):
        super().__init__(parser)
        self.checks = []
        self.parser = parser
        self.checks_dir = checks_dir if checks_dir else \
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "checks")

    def load_checks(self):
        for root, d_names, f_names in os.walk(self.checks_dir):
            for file in f_names:
                file_ending = os.path.splitext(file)[1]
                if file_ending in CHECKS_POSSIBLE_ENDING:
                    with open(f'{root}/{file}', "r") as f:
                        logging.info(f"loading {file}")
                        check_yaml = yaml.safe_load(f)
                        check_json = json.loads(json.dumps(check_yaml))
                        check = self.parser.parse_raw_check(check_json, resources_types=self._get_resource_types(check_json))
                        self.checks.append(check)

    @staticmethod
    def _get_resource_types(check_json):
        provider = check_json.get("scope", {}).get("provider", "").lower()
        return resources_types.get(provider)
