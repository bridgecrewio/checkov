from __future__ import annotations

import itertools
import json
import logging
import re
from collections import defaultdict
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Optional, List

from checkov.common.bridgecrew.code_categories import CodeCategoryType, CodeCategoryMapping
from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.licensing import CustomerLicense, SubscriptionCategoryMapping
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severities
from checkov.common.checks_infra.checks_parser import NXGraphCheckParser
from checkov.common.checks_infra.registry import Registry, get_graph_checks_registry

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.record import Record
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner

# service-provider::service-name::data-type-name
CFN_RESOURCE_TYPE_IDENTIFIER = re.compile(r"^[a-zA-Z0-9]+::[a-zA-Z0-9]+::[a-zA-Z0-9]+$")


class LicensingIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=6)
        self.licensing_type: Optional[str] = None
        self.enabled_code_categories: List[CodeCategoryType] = []
        self.open_source_only: bool = True

    def is_valid(self) -> bool:
        # We will always use this integration to determine what runs or not
        return True

    def pre_scan(self) -> None:
        if not bc_integration.bc_api_key:
            logging.debug('Running without API key, so only open source runners will be enabled')
            self.open_source_only = True
        elif not bc_integration.customer_run_config_response:
            logging.debug('Customer run config response does not exist, but there is an API key, so there may be some integration issue. Proceeding with open source runners.')
            self.open_source_only = True
        else:
            logging.debug('Found customer run config and using it for licensing')
            self.open_source_only = False
            self.licensing_type = 'developer'

            logging.debug(f'Customer license type: {self.licensing_type}')

            if self.licensing_type == CustomerLicense.RESOURCES:
                logging.debug('Customer is on legacy resource licensing, so all frameworks are enabled')
            else:
                logging.debug('Customer is on developer-based licensing')
                enabled_modules = ['iac']
                logging.debug(f'The following modules are enabled: {enabled_modules}')

                self.enabled_code_categories = list(itertools.chain.from_iterable(SubscriptionCategoryMapping.get(m) for m in enabled_modules))

                # for m in enabled_modules:
                #     self.enabled_code_categories += SubscriptionCategoryMapping.get(m)

                logging.debug(f'The following code categories are enabled: {self.enabled_code_categories}')

    def is_runner_valid(self, runner: _BaseRunner):
        if self.licensing_type == CustomerLicense.RESOURCES:
            return True
        else:
            return CodeCategoryMapping[runner.check_type] in self.enabled_code_categories

    def post_runner(self, scan_report: Report) -> None:
        pass

    def pre_runner(self, runner: _BaseRunner) -> None:
        # not used
        pass


integration = LicensingIntegration(bc_integration)
