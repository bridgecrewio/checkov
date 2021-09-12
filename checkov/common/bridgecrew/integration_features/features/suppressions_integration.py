import json
import logging
import re
from itertools import groupby

import requests

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.models.enums import CheckResult
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.http_utils import get_default_get_headers, get_auth_header, extract_error_message


class SuppressionsIntegration(BaseIntegrationFeature):

    def __init__(self, bc_integration):
        super().__init__(bc_integration, order=0)
        self.suppressions = {}
        self.suppressions_url = f"{self.bc_integration.api_url}/api/v1/suppressions"

        # bcorgname_provider_timestamp (ex: companyxyz_aws_1234567891011)
        # the provider may be lower or upper depending on where the policy was created
        self.custom_policy_id_regex = re.compile(r'^[a-zA-Z0-9]+_[a-zA-Z]+_\d{13}$')

    def is_valid(self):
        return self.bc_integration.is_integration_configured() and not self.bc_integration.skip_suppressions \
               and not self.integration_feature_failures

    def pre_scan(self):
        try:
            suppressions = sorted(self._get_suppressions_from_platform(), key=lambda s: s['checkovPolicyId'])
            # group and map by policy ID
            self.suppressions = {policy_id: list(sup) for policy_id, sup in groupby(suppressions, key=lambda s: s['checkovPolicyId'])}
            logging.debug(f'Found {len(self.suppressions)} valid suppressions from the platform.')
        except Exception as e:
            self.integration_feature_failures = True
            logging.debug(f'{e} \nScanning without applying suppressions configured in the platform.', exc_info=True)

    def post_runner(self, scan_report):
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
            return any(self._repo_matches(account) for account in suppression['accountIds'])
        elif type == 'Resources':
            for resource in suppression['resources']:
                if self._repo_matches(resource['accountId']) and resource['resourceId'] == f'{record.repo_file_path}:{record.resource}':
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

        # filter out suppressions that we know just don't apply
        suppressions = [s for s in json.loads(response.content) if self._suppression_valid_for_run(s)]

        for suppression in suppressions:
            if suppression['policyId'] in self.bc_integration.bc_id_mapping:
                suppression['checkovPolicyId'] = self.bc_integration.bc_id_mapping[suppression['policyId']]
            else:
                suppression['checkovPolicyId'] = suppression['policyId']  # custom policy

        return suppressions

    def _suppression_valid_for_run(self, suppression):
        """
        Returns whether this suppression is valid. A suppression is NOT valid if:
        - the policy does not have a checkov ID and does not have an ID matching a custom policy format
        - the suppression type is 'Accounts' and this repo is not included in the account list
        :param suppression:
        :return:
        """
        policyId = suppression['policyId']
        if policyId not in self.bc_integration.bc_id_mapping and not self.custom_policy_id_regex.match(policyId):
            return False

        if suppression['suppressionType'] == 'Accounts':
            if not any(self._repo_matches(account) for account in suppression['accountIds']):
                return False

        return True

    def _repo_matches(self, repo_name):
        # matches xyz_org/repo or org/repo (where xyz is the BC org name and the CLI repo prefix from the platform)
        return re.match(f'^(\\w+_)?{self.bc_integration.repo_id}$', repo_name) is not None


integration = SuppressionsIntegration(bc_integration)
