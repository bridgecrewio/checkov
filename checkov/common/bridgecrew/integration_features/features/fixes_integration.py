from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from itertools import groupby
from typing import TYPE_CHECKING, Any

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.http_utils import extract_error_message, get_default_post_headers

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.record import Record
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner

SUPPORTED_FIX_FRAMEWORKS = ['terraform', 'cloudformation']


class FixesIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=10)
        self.fixes_url = f"{self.bc_integration.api_url}/api/v1/fixes/checkov"

    def is_valid(self) -> bool:
        return (
            self.bc_integration.is_integration_configured()
            and not self.bc_integration.skip_fixes
            and not self.integration_feature_failures
        )

    def post_runner(self, scan_report: Report) -> None:
        try:
            if scan_report.check_type not in SUPPORTED_FIX_FRAMEWORKS:
                return
            self._get_platform_fixes(scan_report)
        except Exception:
            self.integration_feature_failures = True
            logging.debug("Fixes will not be applied.", exc_info=True)

    def _get_platform_fixes(self, scan_report: Report) -> None:

        # We might want to convert this to one call for all results (all files), but then we would also have to deal
        # with repo size issues. Because the primary use case for this at the moment is VSCode integration, which
        # runs one file at a time, this can wait.

        sorted_by_file = sorted(scan_report.failed_checks, key=lambda c: c.file_abs_path)
        for file, sorted_failed_checks in groupby(sorted_by_file, key=lambda c: c.file_abs_path):
            failed_checks = [fc for fc in sorted_failed_checks if fc.check_id in metadata_integration.check_metadata]
            if not failed_checks:
                continue
            with open(file, 'r') as reader:
                file_contents = reader.read()

            fixes = self._get_fixes_for_file(scan_report.check_type, file, file_contents, failed_checks)
            if not fixes:
                continue
            all_fixes = fixes['fixes']

            # a mapping of (checkov_check_id, resource_id) to the failed check Record object for lookup later
            # guaranteed to map to exactly one record
            failed_check_by_check_resource: dict[tuple[str, str], Record] = {
                k: list(v)[0] for k, v in groupby(failed_checks, key=lambda c: (c.check_id, c.resource))
            }

            for fix in all_fixes:
                ckv_id = metadata_integration.get_ckv_id_from_bc_id(fix['policyId'])
                if not ckv_id:
                    logging.debug(f"BC ID {fix['policyId']} has no checkov ID - might be a cloned policy")
                    ckv_id = fix.get('policyId', '')

                failed_check = failed_check_by_check_resource.get((ckv_id, fix['resourceId']))  # type:ignore[arg-type]  # ckv_id is not None here
                if not failed_check:
                    logging.warning(f'Could not find the corresponding failed check for the fix for ID {ckv_id} and resource {fix["resourceId"]}')
                    continue
                failed_check.fixed_definition = fix['fixedDefinition']

    def _get_fixes_for_file(
        self, check_type: str, filename: str, file_contents: str, failed_checks: Iterable[Record]
    ) -> dict[str, Any] | None:
        if not self.bc_integration.bc_source:
            logging.error("Source was not set")
            return None

        errors = list(map(lambda c: {
            'resourceId': c.resource,
            'policyId': metadata_integration.get_bc_id(c.check_id) or c.check_id,
            'startLine': c.file_line_range[0],
            'endLine': c.file_line_range[1]
        }, failed_checks))

        payload = {
            'filePath': filename,
            'fileContent': file_contents,
            'framework': check_type,
            'errors': errors
        }

        headers = merge_dicts(
            get_default_post_headers(self.bc_integration.bc_source, self.bc_integration.bc_source_version),
            {"Authorization": self.bc_integration.get_auth_token()}
        )

        if not self.bc_integration.http:
            raise AttributeError("HTTP manager was not correctly created")

        request = self.bc_integration.http.request("POST", self.fixes_url, headers=headers, body=json.dumps(payload))  # type:ignore[no-untyped-call]

        if request.status != 200:
            error_message = extract_error_message(request)
            raise Exception(f'Get fixes request failed with response code {request.status}: {error_message}')

        logging.debug(f'Response from fixes API: {request.data}')

        fixes: list[dict[str, Any]] = json.loads(request.data) if request.data else None
        if not fixes or not isinstance(fixes, list):
            logging.warning(f'Unexpected fixes API response for file {filename}; skipping fixes for this file')
            return None
        return fixes[0]

    def pre_scan(self) -> None:
        # not used
        pass

    def pre_runner(self, runner: _BaseRunner) -> None:
        # not used
        pass

    def post_scan(self, merged_reports: list[Report]) -> None:
        # not used
        pass


integration = FixesIntegration(bc_integration)
