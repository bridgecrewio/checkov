from __future__ import annotations

import logging
import re
from itertools import groupby
from typing import TYPE_CHECKING

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    integration as metadata_integration
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.models.enums import CheckResult

if TYPE_CHECKING:
    from checkov.common.output.report import Report


class SuppressionsIntegration(BaseIntegrationFeature):

    def __init__(self, bc_integration):
        super().__init__(bc_integration, order=1)  # must be after the policy metadata
        self.suppressions = {}
        self.suppressions_url = f"{self.bc_integration.api_url}/api/v1/suppressions"

        # bcorgname_provider_timestamp (ex: companyxyz_aws_1234567891011)
        # the provider may be lower or upper depending on where the policy was created
        self.custom_policy_id_regex = re.compile(r'^[a-zA-Z0-9]+_[a-zA-Z]+_\d{13}$')
        self.repo_name_regex = None

    def is_valid(self) -> bool:
        return (
            self.bc_integration.is_integration_configured()
            and not self.bc_integration.skip_download
            and not self.integration_feature_failures
        )

    def pre_scan(self) -> None:
        try:
            if not self.bc_integration.customer_run_config_response:
                logging.debug('In the pre-scan for suppressions, but nothing was fetched from the platform')
                self.integration_feature_failures = True
                return

            suppressions = self.bc_integration.customer_run_config_response.get('suppressions')

            for suppression in suppressions:
                if suppression['policyId'] in metadata_integration.bc_to_ckv_id_mapping:
                    suppression['checkovPolicyId'] = metadata_integration.get_ckv_id_from_bc_id(suppression['policyId'])
                else:
                    suppression['checkovPolicyId'] = suppression['policyId']  # custom policy

            self._init_repo_regex()
            suppressions = sorted(suppressions, key=lambda s: s['checkovPolicyId'])

            # group and map by policy ID
            self.suppressions = {policy_id: list(sup) for policy_id, sup in
                                 groupby(suppressions, key=lambda s: s['checkovPolicyId'])}
            logging.debug(f'Found {len(self.suppressions)} valid suppressions from the platform.')
        except Exception:
            self.integration_feature_failures = True
            logging.debug("Scanning without applying suppressions configured in the platform.", exc_info=True)

    def post_runner(self, scan_report: Report) -> None:
        self._apply_suppressions_to_report(scan_report)

    def _apply_suppressions_to_report(self, scan_report: Report) -> None:

        # holds the checks that are still not suppressed
        still_failed_checks = []
        still_passed_checks = []
        for check in scan_report.failed_checks + scan_report.passed_checks:
            relevant_suppressions = self.suppressions.get(check.check_id)

            applied_suppression = self._check_suppressions(check, relevant_suppressions) if relevant_suppressions else None
            if applied_suppression:
                check.check_result = {
                    'result': CheckResult.SKIPPED,
                    'suppress_comment': applied_suppression['comment']
                }
                scan_report.skipped_checks.append(check)
            elif check.check_result['result'] == CheckResult.FAILED:
                still_failed_checks.append(check)
            else:
                still_passed_checks.append(check)

        scan_report.failed_checks = still_failed_checks
        scan_report.passed_checks = still_passed_checks

    def _check_suppressions(self, record, suppressions):
        """
        Checks the specified suppressions against the specified record, returning the first applicable suppression,
        or None of no suppression is applicable.
        :param record:
        :param suppressions:
        :return:
        """
        for suppression in suppressions:
            if self._check_suppression(record, suppression):
                return suppression
        return None

    def _check_suppression(self, record, suppression):
        """
        Returns True if and only if the specified suppression applies to the specified record.
        :param record:
        :param suppression:
        :return:
        """
        if record.check_id != suppression['checkovPolicyId']:
            return False

        type = suppression['suppressionType']

        if type == 'Policy':
            # We already validated the policy ID above
            return True
        elif type == 'Accounts':
            # This should be true, because we validated when we downloaded the policies.
            # But checking here adds some resiliency against bugs if that changes.
            return any(self.bc_integration.repo_matches(account) for account in suppression['accountIds'])
        elif type == 'Resources':
            for resource in suppression['resources']:
                if self.bc_integration.repo_matches(resource['accountId']) \
                        and resource['resourceId'] == f'{record.repo_file_path}:{record.resource}':
                    return True
            return False
        elif type == 'Tags':
            entity_tags = record.entity_tags
            if not entity_tags:
                return False
            suppression_tags = suppression['tags']  # a list of objects of the form {key: str, value: str}

            for tag in suppression_tags:
                key = tag['key']
                value = tag['value']
                if entity_tags.get(key) == value:
                    return True

        return False

    def _suppression_valid_for_run(self, suppression):
        """
        Returns whether this suppression is valid. A suppression is NOT valid if:
        - the policy does not have a checkov ID and does not have an ID matching a custom policy format
        - the suppression type is 'Accounts' and this repo is not included in the account list
        :param suppression:
        :return:
        """
        policyId = suppression['policyId']
        if policyId not in metadata_integration.bc_to_ckv_id_mapping and not self.custom_policy_id_regex.match(
                policyId):
            return False

        if suppression['suppressionType'] == 'Accounts':
            if not any(self.bc_integration.repo_matches(account) for account in suppression['accountIds']):
                return False

        return True

    def _repo_matches(self, repo_name):
        # matches xyz_org/repo or org/repo (where xyz is the BC org name and the CLI repo prefix from the platform)
        return self.repo_name_regex.match(repo_name) is not None

    def _init_repo_regex(self):
        self.repo_name_regex = re.compile(f'^([a-zA-Z0-9]+_)?{self.bc_integration.repo_id}$')


integration = SuppressionsIntegration(bc_integration)
