from __future__ import annotations

import logging
import os
import json
import itertools
from concurrent import futures
from io import StringIO
from typing import Any, TYPE_CHECKING, Optional, Dict
from collections import defaultdict

import dpath
from rustworkx import PyDiGraph, digraph_node_link_json  # type: ignore

try:
    from networkx import DiGraph, node_link_data
except ImportError:
    logging.info("Not able to import networkx")
    DiGraph = str
    node_link_data = lambda G : {}

from checkov.common.sast.consts import CDK_FRAMEWORK_PREFIX, SAST_FRAMEWORK_PREFIX
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS
from checkov.common.typing import _ReducedScanReport, LibraryGraph
from checkov.common.util.file_utils import compress_multiple_strings_ios_tar
from checkov.common.util.json_utils import CustomJSONEncoder

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client

    from checkov.common.output.report import Report

checkov_results_prefix = 'checkov_results'
check_reduced_keys = (
    'check_id', 'check_result', 'resource', 'file_path',
    'file_line_range', 'code_block', 'caller_file_path', 'caller_file_line_range')
secrets_check_reduced_keys = check_reduced_keys + ('validation_status',)
check_metadata_keys = ('evaluations', 'code_block', 'workflow_name', 'triggers', 'job')

FILE_NAME_NETWORKX = 'graph_networkx.json'
FILE_NAME_RUSTWORKX = 'graph_rustworkx.json'


def _is_scanned_file(file: str) -> bool:
    file_ending = os.path.splitext(file)[1]
    return file_ending in SUPPORTED_FILE_EXTENSIONS


def _put_json_object(s3_client: S3Client, json_obj: Any, bucket: str, object_path: str, log_stack_trace_on_error: bool = True) -> None:
    try:
        s3_client.put_object(Bucket=bucket, Key=object_path, Body=json.dumps(json_obj, cls=CustomJSONEncoder))
    except Exception:
        logging.error(f"failed to persist object into S3 bucket {bucket} - {object_path}", exc_info=log_stack_trace_on_error)
        raise


def _extract_checks_metadata(report: Report, full_repo_object_key: str, on_prem: bool) -> dict[str, dict[str, Any]]:
    metadata: dict[str, dict[str, Any]] = defaultdict(dict)
    for check in itertools.chain(report.passed_checks, report.failed_checks, report.skipped_checks):
        metadata_key = f'{check.file_path}:{check.resource}'
        check_meta = {k: getattr(check, k, "") for k in check_metadata_keys}
        check_meta['file_object_path'] = full_repo_object_key + check.file_path
        if on_prem:
            check_meta['code_block'] = []
        metadata[metadata_key][check.check_id] = check_meta

    return metadata


def reduce_scan_reports(scan_reports: list[Report], on_prem: Optional[bool] = False) -> dict[str, _ReducedScanReport]:
    """
    Transform checkov reports objects into compact dictionaries
    :param scan_reports: List of checkov output reports
    :return: dictionary of
    """
    reduced_scan_reports: dict[str, _ReducedScanReport] = {}
    for report in scan_reports:
        check_type = report.check_type
        if check_type.startswith((SAST_FRAMEWORK_PREFIX, CDK_FRAMEWORK_PREFIX)):
            continue
        reduced_keys = secrets_check_reduced_keys if check_type == CheckType.SECRETS else check_reduced_keys
        if on_prem:
            reduced_keys = tuple(k for k in reduced_keys if k != 'code_block')  # type: ignore
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


def persist_assets_results(check_type: str, assets_report: Dict[str, Any], s3_client: Optional[S3Client],
                           bucket: Optional[str], full_repo_object_key: Optional[str]) -> str:
    if not s3_client or not bucket or not full_repo_object_key:
        return ''
    check_result_object_path = f'{full_repo_object_key}/{checkov_results_prefix}/{check_type}/assets.json'
    _put_json_object(s3_client, assets_report, bucket, check_result_object_path)
    return check_result_object_path


def persist_reachability_results(check_type: str, reachability_report: Dict[str, Any], s3_client: Optional[S3Client],
                                 bucket: Optional[str], full_repo_object_key: Optional[str]) -> str:
    if not s3_client or not bucket or not full_repo_object_key:
        return ''
    check_result_object_path = f'{full_repo_object_key}/{checkov_results_prefix}/{check_type}/reachability_report.json'
    _put_json_object(s3_client, reachability_report, bucket, check_result_object_path)
    return check_result_object_path


def persist_checks_results(
        reduced_scan_reports: dict[str, _ReducedScanReport], s3_client: S3Client, bucket: str,
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
        run_metadata: dict[str, str | list[str]], s3_client: S3Client, bucket: str, full_repo_object_key: str, use_checkov_results: bool = True
) -> None:
    object_path = f'{full_repo_object_key}/{checkov_results_prefix}/run_metadata.json' if use_checkov_results else f'{full_repo_object_key}/run_metadata.json'
    try:
        s3_client.put_object(Bucket=bucket, Key=object_path, Body=json.dumps(run_metadata, indent=2))

    except Exception:
        logging.error(f"failed to persist run metadata into S3 bucket {bucket}", exc_info=True)
        raise


def persist_multiple_logs_stream(logs_streams: Dict[str, StringIO], s3_client: S3Client, bucket: str, full_repo_object_key: str) -> None:
    file_io = compress_multiple_strings_ios_tar(logs_streams)
    object_path = f'{full_repo_object_key}/logs_files.tar.gz'
    try:
        s3_client.put_object(Bucket=bucket, Key=object_path, Body=file_io)
    except Exception:
        logging.error(f"failed to persist logs stream into S3 bucket {bucket}", exc_info=True)
        raise


def enrich_and_persist_checks_metadata(
        scan_reports: list[Report], s3_client: S3Client, bucket: str, full_repo_object_key: str, on_prem: bool
) -> dict[str, dict[str, str]]:
    """
    Save checks metadata into bridgecrew's platform
    :return:
    """
    checks_metadata_paths: dict[str, dict[str, str]] = {}
    for scan_report in scan_reports:
        check_type = scan_report.check_type
        if check_type.startswith((SAST_FRAMEWORK_PREFIX, CDK_FRAMEWORK_PREFIX)):
            continue
        checks_metadata_object = _extract_checks_metadata(scan_report, full_repo_object_key, on_prem)
        checks_metadata_object_path = f'{full_repo_object_key}/{checkov_results_prefix}/{check_type}/checks_metadata.json'
        dpath.new(checks_metadata_paths, f"{check_type}/checks_metadata_path", checks_metadata_object_path)
        _put_json_object(s3_client, checks_metadata_object, bucket, checks_metadata_object_path)
    return checks_metadata_paths


def persist_graphs(
        graphs: dict[str, list[tuple[LibraryGraph, Optional[str]]]],
        s3_client: S3Client,
        bucket: str,
        full_repo_object_key: str,
        timeout: int,
        absolute_root_folder: str = ''
) -> None:
    def _upload_graph(check_type: str, graph: LibraryGraph, _absolute_root_folder: str = '', subgraph_path: Optional[str] = None) -> None:
        if isinstance(graph, DiGraph):
            json_obj = node_link_data(graph)
            graph_file_name = FILE_NAME_NETWORKX
        elif isinstance(graph, PyDiGraph):
            json_obj = digraph_node_link_json(graph)
            graph_file_name = FILE_NAME_RUSTWORKX
        else:
            logging.error(f"unsupported graph type '{graph.__class__.__name__}'")
            return
        multi_graph_addition = (f"multi-graph/{subgraph_path}" if subgraph_path is not None else '').rstrip("/")
        s3_key = os.path.join(graphs_repo_object_key, check_type, multi_graph_addition, graph_file_name)
        try:
            _put_json_object(s3_client, json_obj, bucket, s3_key)
        except Exception:
            logging.error(f'failed to upload graph from framework {check_type} to platform', exc_info=True)

    graphs_repo_object_key = full_repo_object_key.replace('checkov', 'graphs')[:-4]

    with futures.ThreadPoolExecutor() as executor:
        futures.wait(
            [executor.submit(_upload_graph, check_type, graph, absolute_root_folder, subgraph_path) for
             check_type, graphs in graphs.items() for graph, subgraph_path in graphs],
            return_when=futures.FIRST_EXCEPTION,
            timeout=timeout
        )
    logging.info(f"Done persisting {len(list(itertools.chain(*graphs.values())))} graphs")


def persist_resource_subgraph_maps(
        resource_subgraph_maps: dict[str, dict[str, str]],
        s3_client: S3Client,
        bucket: str,
        full_repo_object_key: str,
        timeout: int
) -> None:
    def _upload_resource_subgraph_map(check_type: str, resource_subgraph_map: dict[str, str]) -> None:
        s3_key = os.path.join(graphs_repo_object_key, check_type, "multi-graph/resource_subgraph_maps/resource_subgraph_map.json")
        try:
            _put_json_object(s3_client, resource_subgraph_map, bucket, s3_key)
        except Exception:
            logging.error(f'failed to upload resource_subgraph_map from framework {check_type} to platform', exc_info=True)

    # removing '/src' with [:-4]
    graphs_repo_object_key = full_repo_object_key.replace('checkov', 'graphs')[:-4]
    with futures.ThreadPoolExecutor() as executor:
        futures.wait(
            [executor.submit(_upload_resource_subgraph_map, check_type, resource_subgraph_map) for
             check_type, resource_subgraph_map in resource_subgraph_maps.items()],
            return_when=futures.FIRST_EXCEPTION,
            timeout=timeout
        )
    if resource_subgraph_maps:
        logging.info(f"Done persisting resource_subgraph_maps for frameworks - {', '.join(resource_subgraph_maps.keys())}")
