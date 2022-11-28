from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List

from checkov.common.bridgecrew.code_categories import CodeCategoryType, CodeCategoryMapping
from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.licensing import SubscriptionCategoryMapping, \
    CategoryToSubscriptionMapping, CustomerSubscription
from checkov.common.bridgecrew.platform_integration import bc_integration

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner


LICENSE_KEY = 'platformLicense'
GIT_CLONE_ENABLED_KEY = 'gitCloneEnabled'
MODULES_KEY = 'modules'


class LicensingIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=6)
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
            license_details = self.bc_integration.customer_run_config_response.get(LICENSE_KEY)
            logging.debug(f'User license details: {license_details}')

            self.open_source_only = False
            self.enabled_modules = [CustomerSubscription(m) for m, e in license_details.get(MODULES_KEY).items() if e]
            self.git_clone_enabled = license_details[GIT_CLONE_ENABLED_KEY]

    def is_runner_valid(self, runner: str):
        logging.debug(f'Checking if {runner} is valid for license')
        if self.open_source_only:
            enabled = CodeCategoryMapping[runner] in [CodeCategoryType.IAC, CodeCategoryType.SECRETS, CodeCategoryType.SUPPLY_CHAIN]  # new secrets are disabled, but the runner is valid
            logging.debug('Open source mode - the runner is {"en" if enabled else "dis"}abled')
        else:
            sub_type = LicensingIntegration.get_subscription_for_runner(runner)
            enabled = sub_type in self.enabled_modules
            logging.debug(f'Customer mode - the {sub_type} subscription is {"en" if enabled else "dis"}abled')

        return enabled

    def include_old_secrets(self):
        return self.open_source_only or CustomerSubscription.SECRETS in self.enabled_modules

    def include_new_secrets(self):
        return self.git_clone_enabled and CustomerSubscription.SECRETS in self.enabled_modules

    def should_run_image_referencer(self):
        return not self.open_source_only and CustomerSubscription.SCA in self.enabled_modules

    @staticmethod
    def get_subscription_for_runner(runner: str):
        return CategoryToSubscriptionMapping.get(CodeCategoryMapping[runner])

    def post_runner(self, scan_report: Report) -> None:
        pass

    def pre_runner(self, runner: _BaseRunner) -> None:
        pass


integration = LicensingIntegration(bc_integration)
