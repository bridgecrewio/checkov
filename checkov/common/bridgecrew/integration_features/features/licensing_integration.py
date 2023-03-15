from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, cast

from checkov.common.bridgecrew.code_categories import CodeCategoryMapping, CodeCategoryType
from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.licensing import CategoryToSubscriptionMapping, CustomerSubscription, \
    open_source_categories
from checkov.common.bridgecrew.platform_integration import bc_integration

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner


LICENSE_KEY = 'platformLicense'
MODULES_KEY = 'modules'


class LicensingIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=6)
        self.enabled_modules: List[CustomerSubscription] = []
        self.open_source_only: bool = True

    @property
    def billing_plan(self) -> None:
        # Deprecated, already calculated in the BE into the enabled_modules list
        return None

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
            # the API will return True for all modules if they are on resource mode, so we don't actually need the billing plan explicitly here
            self.enabled_modules = [CustomerSubscription(m) for m, e in license_details.get(MODULES_KEY).items() if e]

    def is_runner_valid(self, runner_check_type: str) -> bool:
        logging.debug(f'Checking if {runner_check_type} is valid for license')
        if self.open_source_only:
            enabled = CodeCategoryMapping[runner_check_type] in open_source_categories  # new secrets are disabled, but the runner is valid
            logging.debug(f'Open source mode - the runner is {"en" if enabled else "dis"}abled')
        else:
            sub_type = LicensingIntegration.get_subscription_for_runner(runner_check_type)
            enabled = sub_type in self.enabled_modules
            logging.debug(f'Customer mode - the {sub_type} subscription is {"en" if enabled else "dis"}abled')

        return enabled

    def should_run_image_referencer(self) -> bool:
        return not self.open_source_only and CustomerSubscription.SCA in self.enabled_modules

    @staticmethod
    def get_subscription_for_runner(runner_check_type: str) -> CustomerSubscription:
        if 'sca_' in runner_check_type:
            # SCA runners currently have two CodeCategoryTypes
            return CustomerSubscription.SCA
        else:
            return CategoryToSubscriptionMapping[cast(CodeCategoryType, CodeCategoryMapping[runner_check_type])]

    def post_runner(self, scan_report: Report) -> None:
        pass

    def pre_runner(self, runner: _BaseRunner) -> None:
        pass

    def post_scan(self, merged_reports: list[Report]) -> None:
        # not used
        pass


integration = LicensingIntegration(bc_integration)
