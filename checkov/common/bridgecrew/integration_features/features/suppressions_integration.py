import json
import logging
from itertools import groupby

import requests

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.models.enums import CheckResult
from checkov.common.util.dict_utils import merge_dicts
from checkov.common.util.http_utils import get_default_get_headers, get_auth_header, extract_error_message


class SuppressionsIntegration(BaseIntegrationFeature):

    def __init__(self, bc_integration):
        super().__init__(bc_integration, order=0)
        self.suppressions = {}

    def is_valid(self):
        return self.bc_integration.is_integration_configured() and not self.bc_integration.skip_suppressions

    def pre_scan(self):
        suppressions = sorted(self._get_suppressions_from_platform(), key=lambda s: s['checkovPolicyId'])
        # group and map by policy ID
        self.suppressions = {policy_id: list(sup) for policy_id, sup in groupby(suppressions, key=lambda s: s['checkovPolicyId'])}
        logging.debug(f'Found {len(self.suppressions)} valid suppressions from the platform.')

    def post_scan(self, scan_report):
        self._apply_suppressions_to_report(scan_report)

    def _apply_suppressions_to_report(self, scan_report):

        # holds the checks that are still not suppressed
        still_failed_checks = []
        for failed_check in scan_report.failed_checks:
            relevant_suppressions = self.suppressions.get(failed_check.check_id)

            applied_suppression = self._check_suppressions(failed_check,
                                                          relevant_suppressions) if relevant_suppressions else None
            if applied_suppression:
                failed_check.check_result = {
                    'result': CheckResult.SKIPPED,
                    'suppress_comment': applied_suppression['comment']
                }
                scan_report.skipped_checks.append(failed_check)
            else:
                still_failed_checks.append(failed_check)

        scan_report.failed_checks = still_failed_checks

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
            return self.bc_integration.repo_id in suppression['accountIds']
        elif type == 'Resources':
            for resource in suppression['resources']:
                if resource['accountId'] == self.bc_integration.repo_id and resource['resourceId'] == f'{record.repo_file_path}:{record.resource}':
                    return True
            return False
        elif type == 'Tags':
            entity_tags = record.entity_tags
            if not entity_tags:
                return False
            suppression_tags = suppression['tags'] # a list of objects of the form {key: str, value: str}

            for tag in suppression_tags:
                key = tag['key']
                value = tag['value']
                if entity_tags.get(key) == value:
                    return True

        return False

    def _get_suppressions_from_platform(self):
        headers = merge_dicts(get_default_get_headers(self.bc_integration.bc_source, self.bc_integration.bc_source_version),
                              get_auth_header(self.bc_integration.bc_api_key))
        response = requests.request('GET', self.suppressions_url, headers=headers)

        if response.status_code != 200:
            error_message = extract_error_message(response)
            raise Exception(f'Get suppressions request failed with response code {response.status_code}: {error_message}')

        # filter out custom policies and non-checkov policies
        suppressions = [s for s in json.loads(response.content) if self._suppression_valid_for_run(s)]

        for suppression in suppressions:
            suppression['checkovPolicyId'] = self.bc_integration.bc_id_mapping[suppression['policyId']]

        return suppressions

    def _suppression_valid_for_run(self, suppression):
        """
        Returns whether this suppression is valid. A suppression is NOT valid if:
        - its policy ID is not a Checkov ID, or
        - the suppression type is 'Accounts' and this repo is not included in the account list
        :param suppression:
        :return:
        """

        policyId = suppression['policyId']
        if policyId not in self.bc_integration.bc_id_mapping:
            return False

        if suppression['suppressionType'] == 'Accounts':
            if self.bc_integration.repo_id not in suppression['accountIds']:
                return False

        return True


integration = SuppressionsIntegration(bc_integration)
