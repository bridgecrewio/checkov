from __future__ import annotations

import itertools
import logging
import re
from itertools import groupby
from typing import TYPE_CHECKING, Pattern, Any, Optional

from checkov.common.bridgecrew.check_type import CheckType

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    integration as metadata_integration
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import SCA_PACKAGE_SCAN_CHECK_NAME
from checkov.common.util.file_utils import convert_to_unix_path
from checkov.common.util.str_utils import removeprefix, align_path

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.report import Report
    from checkov.common.output.record import Record
    from checkov.common.typing import _BaseRunner


class SuppressionsIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=2)  # must be after the custom policies integration
        self.suppressions_v2: dict[str, list[dict[str, Any]]] = {}
        self.suppressions: dict[str, list[dict[str, Any]]] = {}

        # bcorgname_provider_timestamp (ex: companyxyz_aws_1234567891011)
        # the provider may be lower or upper depending on where the policy was created
        self.custom_policy_id_regex = re.compile(r'^[a-zA-Z0-9]+_[a-zA-Z]+_\d{13}$')
        self.repo_name_regex: Pattern[str] | None = None

    @property
    def suppressions_url(self) -> str:
        return f"{self.bc_integration.api_url}/api/v1/suppressions"

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
            suppressions_v2 = self.bc_integration.customer_run_config_response.get('suppressionsV2')  # currently just SAST

            for suppression in suppressions:
                suppression['isV1'] = True
                if suppression['policyId'] in metadata_integration.bc_to_ckv_id_mapping:
                    suppression['checkovPolicyId'] = metadata_integration.get_ckv_id_from_bc_id(suppression['policyId'])
                else:
                    suppression['checkovPolicyId'] = suppression['policyId']  # custom policy

            for suppression in suppressions_v2:
                suppression['isV1'] = False
                checkov_ids = []
                for policy_id in suppression['policyIds']:
                    if policy_id in metadata_integration.bc_to_ckv_id_mapping:
                        checkov_ids.append(metadata_integration.bc_to_ckv_id_mapping[policy_id])
                    else:
                        checkov_ids.append(policy_id)  # custom policy - not supported yet
                suppression['checkovPolicyIds'] = checkov_ids

            self._init_repo_regex()
            suppressions = sorted(suppressions, key=lambda s: s['checkovPolicyId'])

            # group and map by policy ID
            self.suppressions = {policy_id: list(sup) for policy_id, sup in
                                 groupby(suppressions, key=lambda s: s['checkovPolicyId'])}

            # map suppressions v2 by checkov ID - because the policy IDs are arrays, we need to map each unique ID in each
            # suppression's policy ID array to its suppressions
            self.suppressions_v2 = SuppressionsIntegration.create_suppression_v2_policy_id_map(suppressions_v2)

            logging.debug('The found suppression v1 rules are:')
            logging.debug(self.suppressions)
            logging.debug('The found suppression v2 rules are:')
            logging.debug(self.suppressions_v2)

        except Exception:
            self.integration_feature_failures = True
            logging.debug("Scanning without applying suppressions configured in the platform.", exc_info=True)

    @staticmethod
    def create_suppression_v2_policy_id_map(suppressions_v2: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        checkov_id_map: dict[str, list[dict[str, Any]]] = {}
        for suppression in suppressions_v2:
            for checkov_id in suppression['checkovPolicyIds']:
                if checkov_id in checkov_id_map:
                    checkov_id_map[checkov_id].append(suppression)
                else:
                    checkov_id_map[checkov_id] = [suppression]
        return checkov_id_map

    def post_runner(self, scan_report: Report) -> None:
        self._apply_suppressions_to_report(scan_report)

    def _apply_suppressions_to_report(self, scan_report: Report) -> None:

        # holds the checks that are still not suppressed
        still_failed_checks = []
        still_passed_checks = []
        for check in scan_report.failed_checks + scan_report.passed_checks:
            # in order to be able to suppress by policy we assign the relevant check id for package / image scan
            # and avoiding licenses vulns
            if scan_report.check_type == CheckType.SCA_PACKAGE and check.check_name == SCA_PACKAGE_SCAN_CHECK_NAME:
                check.check_id = 'BC_VUL_2'
            if scan_report.check_type == CheckType.SCA_IMAGE and check.check_name == SCA_PACKAGE_SCAN_CHECK_NAME:
                check.check_id = 'BC_VUL_1'

            relevant_suppressions = self.suppressions.get(check.check_id)
            relevant_suppressions_v2 = self.suppressions_v2.get(check.check_id)

            has_suppression = relevant_suppressions or relevant_suppressions_v2

            applied_suppression = self._check_suppressions(check, relevant_suppressions, relevant_suppressions_v2) if has_suppression else None
            if applied_suppression:
                suppress_comment = applied_suppression['comment'] if applied_suppression['isV1'] else applied_suppression['justificationComment']
                if self._should_omit_check(applied_suppression):
                    logging.debug(f'Removing check {check.check_id} from the report, comment: {suppress_comment}')
                else:
                    logging.debug(f'Applying suppression to the check {check.check_id} with the comment: {suppress_comment}')
                    check.check_result = {
                        'result': CheckResult.SKIPPED,
                        'suppress_comment': suppress_comment
                    }
                    scan_report.skipped_checks.append(check)
            elif check.check_result['result'] == CheckResult.FAILED:
                still_failed_checks.append(check)
            else:
                still_passed_checks.append(check)

        scan_report.failed_checks = still_failed_checks
        scan_report.passed_checks = still_passed_checks

    @staticmethod
    def _should_omit_check(applied_suppression: dict[str, Any]) -> bool:
        if applied_suppression['isV1']:
            return False
        if applied_suppression['ruleType'] == 'policy':
            return True
        return False

    def _check_suppressions(self, record: Record, suppressions: Optional[list[dict[str, Any]]], suppressions_v2: Optional[list[dict[str, Any]]]) -> dict[str, Any] | None:
        """
        Checks the specified suppressions against the specified record, returning the applied suppression, if any, else None
        :return:
        """
        if suppressions:
            for suppression in suppressions:
                if self._check_suppression(record, suppression):
                    return suppression
        if suppressions_v2:
            for suppression in suppressions_v2:
                if self._check_suppression_v2(record, suppression):
                    return suppression
        return None

    def _check_suppression(self, record: Record, suppression: dict[str, Any]) -> bool:
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
                        and (resource['resourceId'] == f'{record.repo_file_path}:{record.resource}'
                             or resource['resourceId'] == f'{convert_to_unix_path(record.file_path)}:{record.resource}'):
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

        elif type == 'CvesAccounts':
            if 'accountIds' not in suppression:
                return False
            if self.bc_integration.source_id in suppression['accountIds']:
                if record.vulnerability_details and record.vulnerability_details['id'] in suppression['cves']:
                    return True
            return False

        elif type == 'Cves':
            if 'accountIds' not in suppression:
                return False
            if self.bc_integration.repo_id and self.bc_integration.source_id and self.bc_integration.source_id in suppression['accountIds']\
                    and suppression['cves']:
                repo_name = align_path(self.bc_integration.repo_id).split('/')[-1]
                suppression_path = self._get_cve_suppression_path(suppression)
                repo_file_path = align_path(record.repo_file_path)
                file_abs_path = align_path(record.file_abs_path)
                if file_abs_path == suppression_path[1:] or \
                        file_abs_path == suppression_path or \
                        file_abs_path.endswith("".join([repo_name, suppression_path])) or \
                        removeprefix(repo_file_path, '/') == removeprefix(suppression_path, '/'):
                    return any(record.vulnerability_details and record.vulnerability_details['id'] == cve['cve']
                               for cve in suppression['cves'])
            return False

        elif type == 'LicenseType':
            return any(record.vulnerability_details and record.vulnerability_details['license'] == license_type
                       for license_type in suppression.get('licenseTypes', []))

        return False

    @staticmethod
    def normalize_file_path(file_path: str) -> str:
        """
        Returns the file path with a leading slash, if not already present
        """
        return file_path if file_path.startswith('/') else f'/{file_path}'

    def _check_suppression_v2_file(self, record_file_path: str, suppression_file_path: str, suppression_repo_name: str) -> bool:
        return self.bc_integration.repo_matches(suppression_repo_name)\
            and (suppression_file_path == record_file_path or suppression_file_path == convert_to_unix_path(record_file_path))

    def _check_suppression_v2(self, record: Record, suppression: dict[str, Any]) -> bool:
        if record.check_id not in suppression['checkovPolicyIds']:
            return False

        type = suppression['ruleType']

        if type == 'policy':
            # We just checked the policy ID above
            return True
        elif type == 'finding':
            pass  # TODO how to map them?
        elif type == 'file':
            record_file_path = SuppressionsIntegration.normalize_file_path(record.repo_file_path)
            for file_suppression in suppression['files']:
                suppression_file_path = SuppressionsIntegration.normalize_file_path(file_suppression['filePath'])
                if self._check_suppression_v2_file(record_file_path, suppression_file_path, file_suppression.get('repositoryName', '')):
                    return True
        elif type == 'repository':
            return any(self.bc_integration.repo_matches(repo.get('repositoryName', '')) for repo in suppression['repositories'])
        return False

    def _get_cve_suppression_path(self, suppression: dict[str, Any]) -> str:
        suppression_path: str = align_path(suppression['cves'][0]['id'])
        # for handling cases of IR/docker (e.g: '/Dockerfile:/DockerFile.FROM)
        suppression_path_parts = suppression_path.split(':')
        if len(suppression_path_parts) == 2 and suppression_path_parts[1].startswith(suppression_path_parts[0]):
            return suppression_path_parts[0]
        return suppression_path

    def _suppression_valid_for_run(self, suppression: dict[str, Any]) -> bool:
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

    def _repo_matches(self, repo_name: str) -> bool:
        if not self.repo_name_regex:
            # shouldn't happen
            return False

        # matches xyz_org/repo or org/repo (where xyz is the BC org name and the CLI repo prefix from the platform)
        return self.repo_name_regex.match(repo_name) is not None

    def _init_repo_regex(self) -> None:
        self.repo_name_regex = re.compile(f'^([a-zA-Z0-9]+_)?{self.bc_integration.repo_id}$')

    def pre_runner(self, runner: _BaseRunner) -> None:
        # not used
        pass

    def get_policy_level_suppressions(self) -> dict[str, list[str]]:
        policy_level_suppressions = {}
        for check_suppressions in itertools.chain(self.suppressions.values(), self.suppressions_v2.values()):
            for suppression in check_suppressions:
                if (suppression['isV1'] and suppression.get("suppressionType") == "Policy") or (not suppression['isV1'] and suppression.get("ruleType") == "policy"):
                    policy_level_suppressions[suppression['id']] = [suppression['policyId']] if suppression['isV1'] else suppression['policyIds']
        return policy_level_suppressions

    def post_scan(self, merged_reports: list[Report]) -> None:
        # not used
        pass


integration = SuppressionsIntegration(bc_integration)
