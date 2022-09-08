from __future__ import annotations

import logging
import os
import json
import itertools
from typing import Any, TYPE_CHECKING

import dpath.util

from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS
from checkov.common.typing import _ReducedScanReport
from checkov.common.util.json_utils import CustomJSONEncoder

if TYPE_CHECKING:
    from botocore.client import BaseClient  # type:ignore[import]
    from checkov.common.output.report import Report

checkov_results_prefix = 'checkov_results'
check_reduced_keys = (
    'check_id', 'check_result', 'resource', 'file_path',
    'file_line_range')
check_metadata_keys = ('evaluations', 'code_block', 'workflow_name', 'triggers', 'job')


def _is_scanned_file(file: str) -> bool:
    file_ending = os.path.splitext(file)[1]
    return file_ending in SUPPORTED_FILE_EXTENSIONS


def _put_json_object(s3_client: BaseClient, json_obj: Any, bucket: str, object_path: str) -> None:
    try:
        s3_client.put_object(Bucket=bucket, Key=object_path, Body=json.dumps(json_obj, cls=CustomJSONEncoder))
    except Exception:
        logging.error(f"failed to persist object {json_obj} into S3 bucket {bucket}", exc_info=True)
        raise


def _extract_checks_metadata(report: Report, full_repo_object_key: str) -> dict[str, dict[str, Any]]:
    return {check.check_id: dict({k: getattr(check, k, "") for k in check_metadata_keys},
                                 **{'file_object_path': full_repo_object_key + check.file_path}) for check in
            list(itertools.chain(report.passed_checks, report.failed_checks, report.skipped_checks))}


def reduce_scan_reports(scan_reports: list[Report]) -> dict[str, _ReducedScanReport]:
    """
    Transform checkov reports objects into compact dictionaries
    :param scan_reports: List of checkov output reports
    :return: dictionary of
    """
    reduced_scan_reports: dict[str, _ReducedScanReport] = {}
    for report in scan_reports:
        reduced_scan_reports[report.check_type] = \
            {
                "checks": {
                    "passed_checks": [
                        {k: getattr(check, k) for k in check_reduced_keys}
                        for check in report.passed_checks],
                    "failed_checks": [
                        {k: getattr(check, k) for k in check_reduced_keys}
                        for check in report.failed_checks],
                    "skipped_checks": [
                        {k: getattr(check, k) for k in check_reduced_keys}
                        for check in report.skipped_checks]}}
    return reduced_scan_reports


def persist_checks_results(
    reduced_scan_reports: dict[str, _ReducedScanReport], s3_client: BaseClient, bucket: str, full_repo_object_key: str
) -> dict[str, str]:
    """
    Save reduced scan reports into bridgecrew's platform
    :return: List of checks results path of all runners
    """
    checks_results_paths = {}
    for check_type, reduced_report in reduced_scan_reports.items():
        check_result_object_path = f'{full_repo_object_key}/{checkov_results_prefix}/{check_type}/checks_results.json'
        checks_results_paths[check_type] = check_result_object_path
        _put_json_object(s3_client, reduced_report, bucket, check_result_object_path)
    return checks_results_paths


def enrich_and_persist_checks_metadata(
    scan_reports: list[Report], s3_client: BaseClient, bucket: str, full_repo_object_key: str
) -> dict[str, dict[str, str]]:
    """
    Save checks metadata into bridgecrew's platform
    :return:
    """
    checks_metadata_paths: dict[str, dict[str, str]] = {}
    for scan_report in scan_reports:
        check_type = scan_report.check_type
        checks_metadata_object = _extract_checks_metadata(scan_report, full_repo_object_key)
        checks_metadata_object_path = f'{full_repo_object_key}/{checkov_results_prefix}/{check_type}/checks_metadata.json'
        dpath.new(checks_metadata_paths, f"{check_type}/checks_metadata_path", checks_metadata_object_path)
        _put_json_object(s3_client, checks_metadata_object, bucket, checks_metadata_object_path)
    return checks_metadata_paths
