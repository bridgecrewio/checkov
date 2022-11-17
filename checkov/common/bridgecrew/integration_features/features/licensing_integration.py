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
from checkov.common.bridgecrew.licensing import CustomerLicense, SubscriptionCategoryMapping, \
    CategoryToSubscriptionMapping, CustomerSubscription
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severities
from checkov.common.checks_infra.checks_parser import NXGraphCheckParser
from checkov.common.checks_infra.registry import Registry, get_graph_checks_registry

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner

# service-provider::service-name::data-type-name
CFN_RESOURCE_TYPE_IDENTIFIER = re.compile(r"^[a-zA-Z0-9]+::[a-zA-Z0-9]+::[a-zA-Z0-9]+$")


class LicensingIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=6)
        self.licensing_type: Optional[CustomerLicense] = None
        self.enabled_modules: List[CustomerSubscription] = []
        self.open_source_only: bool = True
        self.git_clone_enabled: bool = False

    def is_valid(self) -> bool:
        # We will always use this integration to determine what runs or not
        return True

    def pre_scan(self) -> None:
        if not self.bc_integration.bc_api_key:
            logging.debug('Running without API key, so only open source runners will be enabled')
            self.open_source_only = True
        elif not self.bc_integration.customer_run_config_response:
            logging.debug('Customer run config response does not exist, but there is an API key, so there may be some integration issue. Proceeding with open source runners.')
            self.open_source_only = True
        else:
            logging.debug('Found customer run config and using it for licensing')

            license_details = self.bc_integration.customer_run_config_response.get('license') # TODO

            logging.debug(f'User license details: {license_details}')

            self.open_source_only = False
            self.licensing_type = CustomerLicense(license_details['mode'])

            logging.debug(f'Customer license type: {self.licensing_type}')

            if self.licensing_type == CustomerLicense.RESOURCE:
                logging.debug('Customer is on legacy resource licensing, so all frameworks are enabled')
                self.git_clone_enabled = license_details['git_clone_enabled']
                logging.debug(f'git clone is {"en" if self.git_clone_enabled else "dis"}abled, so new secret signatures will {"" if self.git_clone_enabled else "not "} be used')
            else:
                logging.debug('Customer is on developer-based licensing')
                self.enabled_modules = [CustomerSubscription(m) for m, e in license_details.get('modules').items() if e]
                logging.debug(f'The following modules are enabled: {self.enabled_modules}')

    def is_runner_valid(self, runner: str):
        if self.licensing_type == CustomerLicense.RESOURCE:
            logging.debug(f'Checking if {runner} is valid for license - license type is {CustomerLicense.RESOURCE}, so all runners are valid')
            return True
        elif self.licensing_type == CustomerLicense.DEVELOPER:
            sub_type = LicensingIntegration.get_subscription_for_runner(runner)
            enabled = sub_type in self.enabled_modules
            logging.debug(f'Checking if {runner} is valid for license - the {sub_type} subscription is {"en" if enabled else "dis"}abled')
            return enabled
        else:  # open_source_only is True
            return CodeCategoryMapping[runner] in [CodeCategoryType.IAC, CodeCategoryType.SECRETS, CodeCategoryType.SUPPLY_CHAIN]  # new secrets are disabled, but the runner is valid

    def include_old_secrets(self):
        return self.licensing_type == CustomerLicense.RESOURCE or self.open_source_only or (self.licensing_type == CustomerLicense.DEVELOPER and CustomerSubscription.SECRETS in self.enabled_modules)

    def include_new_secrets(self):
        return (self.licensing_type == CustomerLicense.RESOURCE and self.git_clone_enabled) or (self.licensing_type == CustomerLicense.DEVELOPER and CustomerSubscription.SECRETS in self.enabled_modules)

    def should_run_image_referencer(self):
        return self.licensing_type == CustomerLicense.RESOURCE or (self.licensing_type == CustomerLicense.DEVELOPER and CustomerSubscription.SCA in self.enabled_modules)

    @staticmethod
    def get_subscription_for_runner(runner: str):
        return CategoryToSubscriptionMapping.get(CodeCategoryMapping[runner])

    def post_runner(self, scan_report: Report) -> None:
        pass

    def pre_runner(self, runner: _BaseRunner) -> None:
        # not used
        pass


integration = LicensingIntegration(bc_integration)
