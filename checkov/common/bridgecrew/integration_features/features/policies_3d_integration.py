from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severities
from checkov.policies_3d.checks_parser import Policy3dParser
from checkov.policies_3d.runner import Policy3dRunner

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner


class Policies3DIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=11)
        self.platform_policy_parser = Policy3dParser()

    def is_valid(self) -> bool:
        return (
            self.bc_integration.is_integration_configured()
            and not self.bc_integration.skip_download
            and not self.integration_feature_failures
        )

    def should_run_image_referencer(self) -> bool:
        return True

    def pre_scan(self) -> None:
        # not used
        pass

    def pre_runner(self, runner: _BaseRunner) -> None:
        # not used
        pass

    def post_runner(self, scan_report: Report) -> None:
        # not used
        pass

    @staticmethod
    def _convert_raw_check(policy: dict[str, Any]) -> dict[str, Any]:
        metadata = {
            'id': policy['id'],
            'name': policy['title'],
            'category': policy['category'],
            'guideline': policy['guideline'],
            'severity': policy['severity']
        }
        check = {
            'metadata': metadata,
            'definition': json.loads(policy['code'])
        }
        return check

    def post_scan(self, scan_reports: list[Report]) -> Report | None:
        try:
            if not self.bc_integration.customer_run_config_response:
                logging.debug('In the post scan for 3d policies, but nothing was fetched from the platform')
                self.integration_feature_failures = True
                return None

            policies = self.bc_integration.customer_run_config_response.get('Policies3D')
            logging.debug(f'Got {len(policies)} 3d policies from the platform.')
            checks = []
            runner = Policy3dRunner()
            for policy in policies:
                try:
                    logging.debug(f"Loading 3d policy id: {policy.get('id')}")
                    converted_check = self._convert_raw_check(policy)
                    check = self.platform_policy_parser.parse_raw_check(converted_check)
                    check.severity = Severities[policy['severity']]
                    check.bc_id = check.id
                    checks.append(check)
                except Exception:
                    logging.debug(f"Failed to load 3d policy id: {policy.get('id')}", exc_info=True)

            report = runner.run(checks=checks, scan_reports=scan_reports)
            return report

        except Exception as e:
            self.integration_feature_failures = True
            logging.debug(f'Scanning without applying 3d policies from the platform.\n{e}')
            return None


integration = Policies3DIntegration(bc_integration)
