from __future__ import annotations

import logging
import os
import json
import itertools
from io import StringIO
from typing import Any, TYPE_CHECKING
from collections import defaultdict

import dpath.util

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS
from checkov.common.typing import _ReducedScanReport
from checkov.common.util.file_utils import compress_string_io_tar
from checkov.common.util.json_utils import CustomJSONEncoder

if TYPE_CHECKING:
    from botocore.client import BaseClient  # type:ignore[import]

    from checkov.common.output.report import Report

checkov_results_prefix = 'checkov_results'
check_reduced_keys = (
    'check_id', 'check_result', 'resource', 'file_path',
    'file_line_range')
secrets_check_reduced_keys = check_reduced_keys + ('validation_status',)
check_metadata_keys = ('evaluations', 'code_block', 'workflow_name', 'triggers', 'job')


def _is_scanned_file(file: str) -> bool:
    file_ending = os.path.splitext(file)[1]
    return file_ending in SUPPORTED_FILE_EXTENSIONS


def _put_json_object(s3_client: BaseClient, json_obj: Any, bucket: str, object_path: str) -> None:
    try:
        s3_client.put_object(Bucket=bucket, Key=object_path, Body=json.dumps(json_obj, cls=CustomJSONEncoder))
    except Exception:
        logging.error(f"failed to persist object into S3 bucket {bucket}", exc_info=True)
        raise


def _extract_checks_metadata(report: Report, full_repo_object_key: str) -> dict[str, dict[str, Any]]:
    metadata: dict[str, dict[str, Any]] = defaultdict(dict)
    for check in itertools.chain(report.passed_checks, report.failed_checks, report.skipped_checks):
        metadata_key = f'{check.file_path}:{check.resource}'
        check_meta = {k: getattr(check, k, "") for k in check_metadata_keys}
        check_meta['file_object_path'] = full_repo_object_key + check.file_path
        metadata[metadata_key][check.check_id] = check_meta

    return metadata


def reduce_scan_reports(scan_reports: list[Report]) -> dict[str, _ReducedScanReport]:
    """
    Transform checkov reports objects into compact dictionaries
    :param scan_reports: List of checkov output reports
    :return: dictionary of
    """
    reduced_scan_reports: dict[str, _ReducedScanReport] = {}
    for report in scan_reports:
        check_type = report.check_type
        reduced_keys = secrets_check_reduced_keys if check_type == CheckType.SECRETS else check_reduced_keys
        reduced_scan_reports[check_type] = \
            {
                "checks": {
                    "passed_checks": [
                        {k: getattr(check, k) for k in reduced_keys}
                        for check in report.passed_checks],
                    "failed_checks": [
                        {k: getattr(check, k) for k in reduced_keys}
                        for check in report.failed_checks],
                    "skipped_checks": [
                        {k: getattr(check, k) for k in reduced_keys}
                        for check in report.skipped_checks]
                },
                "image_cached_results": report.image_cached_results
        }
    return reduced_scan_reports


def persist_checks_results(
        reduced_scan_reports: dict[str, _ReducedScanReport], s3_client: BaseClient, bucket: str,
        full_repo_object_key: str
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


def persist_run_metadata(
        run_metadata: dict[str, str | list[str]], s3_client: BaseClient, bucket: str, full_repo_object_key: str
) -> None:
    object_path = f'{full_repo_object_key}/{checkov_results_prefix}/run_metadata.json'
    try:
        s3_client.put_object(Bucket=bucket, Key=object_path, Body=json.dumps(run_metadata, indent=2))

    except Exception:
        logging.error(f"failed to persist run metadata into S3 bucket {bucket}", exc_info=True)
        raise


def persist_logs_stream(logs_stream: StringIO, s3_client: BaseClient, bucket: str, full_repo_object_key: str) -> None:
    file_io = compress_string_io_tar(logs_stream)
    object_path = f'{full_repo_object_key}/{checkov_results_prefix}/logs_file.tar.gz'
    try:
        s3_client.put_object(Bucket=bucket, Key=object_path, Body=file_io)
    except Exception:
        logging.error(f"failed to persist logs stream into S3 bucket {bucket}", exc_info=True)
        raise


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
