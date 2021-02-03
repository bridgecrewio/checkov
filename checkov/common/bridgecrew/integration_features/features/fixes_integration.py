import logging
from itertools import groupby

import json
import os
import requests

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.util.dict_utils import merge_dicts
from checkov.common.util.http_utils import get_auth_header, extract_error_message, \
    get_default_post_headers

SUPPORTED_FIX_FRAMEWORKS = ['terraform', 'cloudformation']


class FixesIntegration(BaseIntegrationFeature):

    def __init__(self, bc_integration):
        super().__init__(bc_integration, order=10)

    def is_valid(self):
        return self.bc_integration.is_integration_configured() and not self.bc_integration.skip_fixes

    def post_scan(self, scan_report):
        if scan_report.check_type not in SUPPORTED_FIX_FRAMEWORKS:
            return
        self._get_platform_fixes(scan_report)

    def _get_platform_fixes(self, scan_report):

        # We might want to convert this to one call for all results (all files), but then we would also have to deal
        # with repo size issues. Because the primary use case for this at the moment is VSCode integration, which
        # runs one file at a time, this can wait.

        sorted_by_file = sorted(scan_report.failed_checks, key=lambda c: c.repo_file_path)
        for file, failed_checks in groupby(sorted_by_file, key=lambda c: c.repo_file_path):
            failed_checks = [fc for fc in failed_checks if fc.check_id in self.bc_integration.ckv_to_bc_id_mapping]
            if not failed_checks:
                continue
            # file path always starts with /
            file_abs_path = os.path.abspath(os.path.join(os.getcwd(), file[1:]))
            with open(file_abs_path, 'r') as reader:
                file_contents = reader.read()

            fixes = self._get_fixes_for_file(file, file_contents, failed_checks)
            if not fixes:
                continue
            all_fixes = fixes['fixes']

            # a mapping of (checkov_check_id, resource_id) to the failed check Record object for lookup later
            # guaranteed to map to exactly one record
            failed_check_by_check_resource = {k: list(v)[0] for k, v in groupby(failed_checks, key=lambda c: (c.check_id, c.resource))}

            for fix in all_fixes:
                ckv_id = self.bc_integration.bc_id_mapping[fix['policyId']]
                failed_check = failed_check_by_check_resource[(ckv_id, fix['resourceId'])]
                failed_check.fixed_definition = fix['fixedDefinition']

    def _get_fixes_for_file(self, filename, file_contents, failed_checks):

        errors = list(map(lambda c: {
            'resourceId': c.resource,
            'policyId': self.bc_integration.ckv_to_bc_id_mapping[c.check_id],
            'startLine': c.file_line_range[0],
            'endLine': c.file_line_range[1]
        }, failed_checks))

        payload = {
            'filePath': filename,
            'fileContent': file_contents,
            'errors': errors
        }

        headers = merge_dicts(get_default_post_headers(self.bc_integration.bc_source, self.bc_integration.bc_source_version),
                              get_auth_header(self.bc_integration.bc_api_key))

        response = requests.request('POST', self.fixes_url, headers=headers, json=payload)

        if response.status_code != 200:
            error_message = extract_error_message(response)
            raise Exception(f'Get fixes request failed with response code {response.status_code}: {error_message}')

        logging.debug(f'Response from fixes API: {response.content}')

        fixes = json.loads(response.content) if response.content else None
        if not fixes or type(fixes) != list:
            logging.warning(f'Unexpected fixes API response for file {filename}; skipping fixes for this file')
            return None
        return fixes[0]


integration = FixesIntegration(bc_integration)
