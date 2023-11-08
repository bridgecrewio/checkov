from __future__ import annotations

import json
import logging
import os.path
import re
import uuid
from collections import namedtuple
from concurrent import futures
from io import StringIO
from json import JSONDecodeError
from os import path
from pathlib import Path
from time import sleep
from typing import List, Dict, TYPE_CHECKING, Any, cast, Optional, Union
from urllib.parse import urlparse

import boto3
import dpath
import urllib3
from botocore.config import Config
from botocore.exceptions import ClientError
from cachetools import cached, TTLCache
from colorama import Style
from termcolor import colored
from tqdm import trange
from urllib3.exceptions import HTTPError, MaxRetryError

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.platform_errors import BridgecrewAuthError
from checkov.common.bridgecrew.platform_key import read_key
from checkov.common.bridgecrew.run_metadata.registry import registry
from checkov.common.bridgecrew.wrapper import persist_assets_results, reduce_scan_reports, persist_checks_results, \
    enrich_and_persist_checks_metadata, checkov_results_prefix, persist_run_metadata, _put_json_object, \
    persist_logs_stream, persist_graphs, persist_resource_subgraph_maps, persist_reachability_results
from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS, SUPPORTED_FILES, SCANNABLE_PACKAGE_FILES
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.common.typing import _CicdDetails, LibraryGraph
from checkov.common.util.consts import PRISMA_PLATFORM, BRIDGECREW_PLATFORM, CHECKOV_RUN_SCA_PACKAGE_SCAN_V2
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.dockerfile import is_dockerfile
from checkov.common.util.http_utils import (
    normalize_prisma_url,
    get_auth_header,
    get_default_get_headers,
    get_user_agent_header,
    get_default_post_headers,
    get_prisma_get_headers,
    get_prisma_auth_header,
    get_auth_error_message,
    normalize_bc_url,
    REQUEST_CONNECT_TIMEOUT,
    REQUEST_READ_TIMEOUT,
    REQUEST_RETRIES,
)
from checkov.common.util.type_forcers import convert_prisma_policy_filter_to_dict, convert_str_to_bool
from checkov.version import version as checkov_version

if TYPE_CHECKING:
    import argparse
    from checkov.common.bridgecrew.bc_source import SourceType
    from checkov.common.output.report import Report
    from checkov.secrets.coordinator import EnrichedSecret
    from mypy_boto3_s3.client import S3Client
    from typing_extensions import TypeGuard

SLEEP_SECONDS = 1

EMAIL_PATTERN = re.compile(r"[^@]+@[^@]+\.[^@]+")
UUID_V4_PATTERN = re.compile(r"^[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}$")
# found at https://regexland.com/base64/
BASE64_PATTERN = re.compile(r"^(?:[A-Za-z\d+/]{4})*(?:[A-Za-z\d+/]{3}=|[A-Za-z\d+/]{2}==)?$")
REPO_PATH_PATTERN = re.compile(r'checkov/(.*?)/src')

ACCOUNT_CREATION_TIME = 180  # in seconds

UNAUTHORIZED_MESSAGE = 'User is not authorized to access this resource with an explicit deny'
ASSUME_ROLE_UNUATHORIZED_MESSAGE = 'is not authorized to perform: sts:AssumeRole'

FileToPersist = namedtuple('FileToPersist', 'full_file_path s3_file_key')

DEFAULT_REGION = "us-west-2"
GOV_CLOUD_REGION = 'us-gov-west-1'
PRISMA_GOV_API_URL = 'https://api.gov.prismacloud.io'
MAX_RETRIES = 40

CI_METADATA_EXTRACTOR = registry.get_extractor()


class BcPlatformIntegration:
    def __init__(self) -> None:
        self.bc_api_key = read_key()
        self.s3_client: S3Client | None = None
        self.bucket: str | None = None
        self.credentials: dict[str, str] | None = None
        self.repo_path: str | None = None
        self.support_bucket: str | None = None
        self.support_repo_path: str | None = None
        self.repo_id: str | None = None
        self.repo_branch: str | None = None
        self.skip_fixes = False  # even though we removed the CLI flag, this gets set so we know whether this is a fix run (IDE) or not (normal CLI)
        self.skip_download = False
        self.source_id: str | None = None
        self.bc_source: SourceType | None = None
        self.bc_source_version: str | None = None
        self.timestamp: str | None = None
        self.scan_reports: list[Report] = []
        self.bc_api_url = normalize_bc_url(os.getenv('BC_API_URL', "https://www.bridgecrew.cloud"))
        self.prisma_api_url = normalize_prisma_url(os.getenv("PRISMA_API_URL"))
        self.prisma_policies_url: str | None = None
        self.prisma_policy_filters_url: str | None = None
        self.setup_api_urls()
        self.customer_run_config_response = None
        self.prisma_policies_response = None
        self.public_metadata_response = None
        self.use_s3_integration = False
        self.s3_setup_failed = False
        self.platform_integration_configured = False
        self.http: urllib3.PoolManager | urllib3.ProxyManager | None = None
        self.http_timeout = urllib3.Timeout(connect=REQUEST_CONNECT_TIMEOUT, read=REQUEST_READ_TIMEOUT)
        self.http_retry = urllib3.Retry(REQUEST_RETRIES, redirect=3)
        self.bc_skip_mapping = False
        self.cicd_details: _CicdDetails = {}
        self.support_flag_enabled = False
        self.enable_persist_graphs = convert_str_to_bool(os.getenv('BC_ENABLE_PERSIST_GRAPHS', 'True'))
        self.persist_graphs_timeout = int(os.getenv('BC_PERSIST_GRAPHS_TIMEOUT', 60))
        self.ca_certificate: str | None = None
        self.no_cert_verify: bool = False
        self.on_prem: bool = False

    def set_bc_api_url(self, new_url: str) -> None:
        self.bc_api_url = normalize_bc_url(new_url)
        self.setup_api_urls()

    def setup_api_urls(self) -> None:
        """
        API URLs vary depending upon whether the platform is Bridgecrew or Prisma Cloud.
        Bridgecrew has one default that can be used when initializing the class,
        but Prisma Cloud requires resetting them in setup_bridgecrew_credentials,
        which is where command-line parameters are first made available.
        """
        if self.prisma_api_url:
            self.api_url = f"{self.prisma_api_url}/bridgecrew"
            self.prisma_policies_url = f"{self.prisma_api_url}/v2/policy"
            self.prisma_policy_filters_url = f"{self.prisma_api_url}/filter/policy/suggest"
        else:
            self.api_url = self.bc_api_url
        self.guidelines_api_url = f"{self.api_url}/api/v2/guidelines"
        self.guidelines_api_url_backoff = f"{self.api_url}/api/v1/guidelines"

        self.integrations_api_url = f"{self.api_url}/api/v1/integrations/types/checkov"
        self.platform_run_config_url = f"{self.api_url}/api/v2/checkov/runConfiguration"
        self.reachability_run_config_url = f"{self.api_url}/api/v2/checkov/reachabilityRunConfiguration"

    def is_prisma_integration(self) -> bool:
        if self.bc_api_key and not self.is_bc_token(self.bc_api_key):
            return True
        return False

    @staticmethod
    def is_token_valid(token: str) -> bool:
        parts = token.split('::')
        parts_len = len(parts)
        if parts_len == 1:
            valid = BcPlatformIntegration.is_bc_token(token)
            # TODO: add it back at a later time
            # if valid:
            #     print(
            #         "We're glad you're using Checkov with Bridgecrew!\n"
            #         "Bridgecrew has been fully integrated into Prisma Cloud with a powerful code to cloud experience.\n"
            #         "As a part of the transition, we will be shutting down Bridgecrew standalone edition at the end of 2023 (https://www.paloaltonetworks.com/services/support/end-of-life-announcements).\n"
            #         "Please upgrade to Prisma Cloud Enterprise Edition before the end of the year.\n"
            #     )

            return valid
        elif parts_len == 2:
            # A Prisma access key is a UUID, same as a BC API key
            if BcPlatformIntegration.is_bc_token(parts[0]) and parts[1] and BASE64_PATTERN.match(parts[1]) is not None:
                return True
            return False
        else:
            return False

    @staticmethod
    def is_bc_token(token: str | None) -> TypeGuard[str]:
        if not token:
            return False

        return re.match(UUID_V4_PATTERN, token) is not None

    @cached(TTLCache(maxsize=1, ttl=540))
    def get_auth_token(self) -> str:
        if self.is_bc_token(self.bc_api_key):
            return self.bc_api_key
        # A Prisma Cloud Access Key was specified as the Bridgecrew token.
        if not self.prisma_api_url:
            raise ValueError("A Prisma Cloud token was set, but no Prisma Cloud API URL was set")
        if not self.bc_api_key:
            # should usually not happen
            raise ValueError("A Prisma Cloud or Birdgecrew token was not set")
        if '::' not in self.bc_api_key:
            raise ValueError(
                "A Prisma Cloud token was set, but the token is not in the correct format: <access_key_id>::<secret_key>")
        if not self.http:
            raise AttributeError("HTTP manager was not correctly created")
        username, password = self.bc_api_key.split('::')
        request = self.http.request("POST", f"{self.prisma_api_url}/login",  # type:ignore[no-untyped-call]
                                    body=json.dumps({"username": username, "password": password}),
                                    headers=merge_dicts({"Content-Type": "application/json"}, get_user_agent_header()))
        if request.status == 401:
            logging.error(f'Received 401 response from Prisma /login endpoint: {request.data.decode("utf8")}')
            raise BridgecrewAuthError()
        elif request.status == 403:
            logging.error('Received 403 (Forbidden) response from Prisma /login endpoint')
            raise BridgecrewAuthError()
        token: str = json.loads(request.data.decode("utf8"))['token']
        return token

    def setup_http_manager(self, ca_certificate: str | None = None, no_cert_verify: bool = False) -> None:
        """
        bridgecrew uses both the urllib3 and requests libraries, while checkov uses the requests library.
        :param ca_certificate: an optional CA bundle to be used by both libraries.
        :param no_cert_verify: whether to skip SSL cert verification
        """
        self.ca_certificate = ca_certificate
        self.no_cert_verify = no_cert_verify

        ca_certificate = ca_certificate or os.getenv('BC_CA_BUNDLE')
        cert_reqs: str | None

        if self.http:
            return
        if ca_certificate:
            os.environ['REQUESTS_CA_BUNDLE'] = ca_certificate
            cert_reqs = 'CERT_NONE' if no_cert_verify else 'REQUIRED'
            logging.debug(f'Using CA cert {ca_certificate} and cert_reqs {cert_reqs}')
            try:
                parsed_url = urllib3.util.parse_url(os.environ['https_proxy'])
                self.http = urllib3.ProxyManager(
                    os.environ['https_proxy'],
                    cert_reqs=cert_reqs,
                    ca_certs=ca_certificate,
                    proxy_headers=urllib3.make_headers(proxy_basic_auth=parsed_url.auth),  # type:ignore[no-untyped-call]
                    timeout=self.http_timeout,
                    retries=self.http_retry,
                )
            except KeyError:
                self.http = urllib3.PoolManager(
                    cert_reqs=cert_reqs,
                    ca_certs=ca_certificate,
                    timeout=self.http_timeout,
                    retries=self.http_retry,
                )
        else:
            cert_reqs = 'CERT_NONE' if no_cert_verify else None
            logging.debug(f'Using cert_reqs {cert_reqs}')
            try:
                parsed_url = urllib3.util.parse_url(os.environ['https_proxy'])
                self.http = urllib3.ProxyManager(
                    os.environ['https_proxy'],
                    cert_reqs=cert_reqs,
                    proxy_headers=urllib3.make_headers(proxy_basic_auth=parsed_url.auth),  # type:ignore[no-untyped-call]
                    timeout=self.http_timeout,
                    retries=self.http_retry,
                )
            except KeyError:
                self.http = urllib3.PoolManager(
                    cert_reqs=cert_reqs,
                    timeout=self.http_timeout,
                    retries=self.http_retry,
                )
        logging.debug('Successfully set up HTTP manager')

    def setup_bridgecrew_credentials(
        self,
        repo_id: str,
        skip_download: bool = False,
        source: SourceType | None = None,
        skip_fixes: bool = False,
        source_version: str | None = None,
        repo_branch: str | None = None,
        prisma_api_url: str | None = None,
    ) -> None:
        """
        Setup credentials against Bridgecrew's platform.
        :param repo_id: Identity string of the scanned repository, of the form <repo_owner>/<repo_name>
        :param skip_download: whether to skip downloading data (guidelines, custom policies, etc) from the platform
        :param source:
        :param prisma_api_url: optional URL for the Prisma Cloud platform, requires a Prisma Cloud Access Key as bc_api_key
        """
        self.repo_id = repo_id
        self.repo_branch = repo_branch
        self.skip_fixes = skip_fixes
        self.skip_download = skip_download
        self.bc_source = source
        self.bc_source_version = source_version

        if prisma_api_url:
            self.prisma_api_url = normalize_prisma_url(prisma_api_url)
            self.setup_api_urls()
            logging.info(f'Using Prisma API URL: {self.prisma_api_url}')

        if self.bc_source and self.bc_source.upload_results:
            self.set_s3_integration()

        self.platform_integration_configured = True

    def set_s3_integration(self) -> None:
        region = DEFAULT_REGION
        use_accelerate_endpoint = True
        if self.prisma_api_url == PRISMA_GOV_API_URL:
            region = GOV_CLOUD_REGION
            use_accelerate_endpoint = False

        try:
            self.skip_fixes = True  # no need to run fixes on CI integration
            repo_full_path, support_path, response = self.get_s3_role(self.repo_id)  # type: ignore
            if not repo_full_path:  # happens if the setup fails with something other than an auth error - we continue locally
                return

            self.bucket, self.repo_path = repo_full_path.split("/", 1)

            self.timestamp = self.repo_path.split("/")[-2]
            self.credentials = cast("dict[str, str]", response["creds"])
            config = Config(
                s3={
                    "use_accelerate_endpoint": use_accelerate_endpoint,
                }
            )
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.credentials["AccessKeyId"],
                aws_secret_access_key=self.credentials["SecretAccessKey"],
                aws_session_token=self.credentials["SessionToken"],
                region_name=region,
                config=config,
            )

            if support_path:
                self.support_bucket, self.support_repo_path = support_path.split("/", 1)
            elif self.support_flag_enabled:
                logging.debug(
                    '--support was used, but we did not get a support file upload path in the platform response. Using the old location.')
                self.support_bucket = self.bucket
                self.support_repo_path = self.repo_path

            self.use_s3_integration = True
        except MaxRetryError:
            logging.error("An SSL error occurred connecting to the platform. If you are on a VPN, please try "
                          "disabling it and re-running the command.", exc_info=True)
            raise
        except HTTPError:
            logging.error("Failed to get customer assumed role", exc_info=True)
            raise
        except ClientError:
            logging.error(f"Failed to initiate client with credentials {self.credentials}", exc_info=True)
            raise
        except JSONDecodeError:
            logging.error(f"Response of {self.integrations_api_url} is not a valid JSON", exc_info=True)
            raise
        except BridgecrewAuthError:
            logging.error("Received an error response during authentication")
            raise

    def get_s3_role(self, repo_id: str) -> tuple[str, str, dict[str, Any]] | tuple[None, None, dict[str, Any]]:
        token = self.get_auth_token()

        if not self.http:
            raise AttributeError("HTTP manager was not correctly created")

        tries = 0
        response = self._get_s3_creds(repo_id, token)
        while ('Message' in response or 'message' in response):
            if response.get('Message') and response['Message'] == UNAUTHORIZED_MESSAGE:
                raise BridgecrewAuthError()
            elif response.get('message') and ASSUME_ROLE_UNUATHORIZED_MESSAGE in response['message']:
                raise BridgecrewAuthError(
                    "Checkov got an unexpected authorization error that may not be due to your credentials. Please contact support.")
            elif response.get('message') and "cannot be found" in response['message']:
                self.loading_output("creating role")
                response = self._get_s3_creds(repo_id, token)
            else:
                if tries < 3:
                    tries += 1
                    response = self._get_s3_creds(repo_id, token)
                else:
                    logging.error('Checkov got an unexpected error that may be due to backend issues. The scan will continue, '
                                  'but results will not be sent to the platform. Please contact support for assistance.')
                    logging.error(f'Error from platform: {response.get("message") or response.get("Message")}')
                    self.s3_setup_failed = True
                    return None, None, response
        repo_full_path = response["path"]
        support_path = response.get("supportPath")
        return repo_full_path, support_path, response

    def _get_s3_creds(self, repo_id: str, token: str) -> dict[str, Any]:
        logging.debug(f'Getting S3 upload credentials from {self.integrations_api_url}')
        request = self.http.request("POST", self.integrations_api_url,  # type:ignore[union-attr]
                                    body=json.dumps({"repoId": repo_id, "support": self.support_flag_enabled}),
                                    headers=merge_dicts({"Authorization": token, "Content-Type": "application/json"},
                                                        get_user_agent_header()))
        logging.debug(f'Request ID: {request.headers.get("x-amzn-requestid")}')
        logging.debug(f'Trace ID: {request.headers.get("x-amzn-trace-id")}')
        if request.status == 403:
            error_message = get_auth_error_message(request.status, self.is_prisma_integration(), True)
            raise BridgecrewAuthError(error_message)
        response: dict[str, Any] = json.loads(request.data.decode("utf8"))
        return response

    def is_integration_configured(self) -> bool:
        """
        Checks if Bridgecrew integration is fully configured based in input params.
        :return: True if the integration is configured, False otherwise
        """
        return self.platform_integration_configured

    def persist_repository(
        self,
        root_dir: str | Path,
        files: list[str] | None = None,
        excluded_paths: list[str] | None = None,
        included_paths: list[str] | None = None,
    ) -> None:
        """
        Persist the repository found on root_dir path to Bridgecrew's platform. If --file flag is used, only files
        that are specified will be persisted.
        :param files: Absolute path of the files passed in the --file flag.
        :param root_dir: Absolute path of the directory containing the repository root level.
        :param excluded_paths: Paths to exclude from persist process
        :param included_paths: Paths to exclude from persist process
        """
        excluded_paths = excluded_paths if excluded_paths is not None else []

        if not self.use_s3_integration or self.s3_setup_failed:
            return
        files_to_persist: List[FileToPersist] = []
        if files:
            for f in files:
                f_name = os.path.basename(f)
                _, file_extension = os.path.splitext(f)
                if CHECKOV_RUN_SCA_PACKAGE_SCAN_V2 and file_extension in SCANNABLE_PACKAGE_FILES:
                    continue
                if file_extension in SUPPORTED_FILE_EXTENSIONS or f_name in SUPPORTED_FILES:
                    files_to_persist.append(FileToPersist(f, os.path.relpath(f, root_dir)))
        else:
            for root_path, d_names, f_names in os.walk(root_dir):
                # self.excluded_paths only contains the config fetched from the platform.
                # but here we expect the list from runner_registry as well (which includes self.excluded_paths).
                filter_ignored_paths(root_path, d_names, excluded_paths, included_paths=included_paths)
                filter_ignored_paths(root_path, f_names, excluded_paths)
                for file_path in f_names:
                    _, file_extension = os.path.splitext(file_path)
                    if CHECKOV_RUN_SCA_PACKAGE_SCAN_V2 and file_extension in SCANNABLE_PACKAGE_FILES:
                        continue
                    if file_extension in SUPPORTED_FILE_EXTENSIONS or file_path in SUPPORTED_FILES or is_dockerfile(file_path):
                        full_file_path = os.path.join(root_path, file_path)
                        relative_file_path = os.path.relpath(full_file_path, root_dir)
                        files_to_persist.append(FileToPersist(full_file_path, relative_file_path))

        self.persist_files(files_to_persist)

    def persist_git_configuration(self, root_dir: str | Path, git_config_folders: list[str]) -> None:
        if not self.use_s3_integration or self.s3_setup_failed:
            return
        files_to_persist: list[FileToPersist] = []

        for git_config_folder in git_config_folders:
            if not os.path.isdir(git_config_folder):
                continue
            if not len(os.listdir(git_config_folder)):
                continue

            for root_path, _, f_names in os.walk(git_config_folder):
                for file_path in f_names:
                    _, file_extension = os.path.splitext(file_path)
                    if file_extension in SUPPORTED_FILE_EXTENSIONS:
                        full_file_path = os.path.join(root_path, file_path)
                        relative_file_path = os.path.relpath(full_file_path, root_dir)
                        files_to_persist.append(FileToPersist(full_file_path, relative_file_path))

        self.persist_files(files_to_persist)

    def persist_scan_results(self, scan_reports: list[Report]) -> None:
        """
        Persist checkov's scan result into bridgecrew's platform.
        :param scan_reports: List of checkov scan reports
        """
        if not self.use_s3_integration or not self.s3_client or self.s3_setup_failed:
            return
        if not self.bucket or not self.repo_path:
            logging.error(f"Something went wrong: bucket {self.bucket}, repo path {self.repo_path}")
            return

        # just process reports with actual results in it
        self.scan_reports = [scan_report for scan_report in scan_reports if not scan_report.is_empty(full=True)]

        reduced_scan_reports = reduce_scan_reports(self.scan_reports, self.on_prem)
        checks_metadata_paths = enrich_and_persist_checks_metadata(self.scan_reports, self.s3_client, self.bucket,
                                                                   self.repo_path, self.on_prem)
        dpath.merge(reduced_scan_reports, checks_metadata_paths)
        persist_checks_results(reduced_scan_reports, self.s3_client, self.bucket, self.repo_path)

    async def persist_reachability_alias_mapping(self, alias_mapping: Dict[str, Any]) -> None:
        if not self.use_s3_integration or not self.s3_client or self.s3_setup_failed:
            return
        if not self.bucket or not self.repo_path:
            logging.error(f"Something went wrong: bucket {self.bucket}, repo path {self.repo_path}")
            return

        s3_path = f'{self.repo_path}/alias_mapping.json'
        _put_json_object(self.s3_client, alias_mapping, self.bucket, s3_path)

    def persist_assets_scan_results(self, assets_report: Optional[Dict[str, Any]]) -> None:
        if not assets_report:
            return
        for lang, assets in assets_report['imports'].items():
            new_report = {'imports': {lang.value: assets}}
            persist_assets_results(f'sast_{lang.value}', new_report, self.s3_client, self.bucket, self.repo_path)

    def persist_reachability_scan_results(self, reachability_report: Optional[Dict[str, Any]]) -> None:
        if not reachability_report:
            return
        for lang, report in reachability_report.items():
            persist_reachability_results(f'sast_{lang}', {lang: report}, self.s3_client, self.bucket, self.repo_path)

    def persist_image_scan_results(self, report: dict[str, Any] | None, file_path: str, image_name: str, branch: str) -> None:
        if not self.s3_client:
            logging.error("S3 upload was not correctly initialized")
            return
        if not self.bucket or not self.repo_path:
            logging.error("Bucket or repo_path was not set")
            return

        repo_path_without_src = os.path.dirname(self.repo_path)
        target_report_path = f'{repo_path_without_src}/{checkov_results_prefix}/{CheckType.SCA_IMAGE}/raw_results.json'
        to_upload = {"report": report, "file_path": file_path, "image_name": image_name, "branch": branch}
        _put_json_object(self.s3_client, to_upload, self.bucket, target_report_path)

    def persist_enriched_secrets(self, enriched_secrets: list[EnrichedSecret]) -> str | None:
        if not enriched_secrets or not self.repo_path or not self.bucket:
            logging.debug(f'One of enriched secrets, repo path, or bucket are empty, aborting. values:'
                          f'enriched_secrets={"Valid" if enriched_secrets else "Empty"},'
                          f' repo_path={self.repo_path}, bucket={self.bucket}')
            return None

        if not bc_integration.bc_api_key or not os.getenv("CKV_VALIDATE_SECRETS"):
            logging.debug('Skipping persistence of enriched secrets object as secrets verification is off,'
                          ' enabled it via env var CKV_VALIDATE_SECRETS and provide an api key')
            return None

        if not self.s3_client:
            logging.error("S3 upload was not correctly initialized")
            return None

        base_path = re.sub(REPO_PATH_PATTERN, r'original_secrets/\1', self.repo_path)
        s3_path = f'{base_path}/{uuid.uuid4()}.json'
        try:
            _put_json_object(self.s3_client, enriched_secrets, self.bucket, s3_path, log_stack_trace_on_error=False)
        except ClientError:
            logging.warning("Got access denied, retrying as s3 role changes should be propagated")
            sleep(4)
            try:
                _put_json_object(self.s3_client, enriched_secrets, self.bucket, s3_path, log_stack_trace_on_error=False)
            except ClientError:
                logging.error("Getting access denied consistently, skipping secrets verification, please try again")
                return None

        return s3_path

    def persist_run_metadata(self, run_metadata: dict[str, str | list[str]]) -> None:
        if not self.use_s3_integration or not self.s3_client or self.s3_setup_failed:
            return
        if not self.bucket or not self.repo_path:
            logging.error(f"Something went wrong: bucket {self.bucket}, repo path {self.repo_path}")
            return
        persist_run_metadata(run_metadata, self.s3_client, self.bucket, self.repo_path, True)
        # only upload it if we did not fall back to use the same location
        if self.support_bucket and self.support_repo_path and self.support_repo_path != self.repo_path:
            logging.debug('Also uploading run_metadata.json to support location')
            persist_run_metadata(run_metadata, self.s3_client, self.support_bucket, self.support_repo_path, False)

    def persist_logs_stream(self, logs_stream: StringIO) -> None:
        if not self.use_s3_integration or not self.s3_client or self.s3_setup_failed:
            return
        if not self.support_bucket or not self.support_repo_path:
            logging.error(
                f"Something went wrong with the log upload location: bucket {self.support_bucket}, repo path {self.support_repo_path}")
            return
        # use checkov_results if we fall back to using the same location
        log_path = f'{self.support_repo_path}/checkov_results' if self.support_repo_path == self.repo_path else self.support_repo_path
        persist_logs_stream(logs_stream, self.s3_client, self.support_bucket, log_path)

    def persist_graphs(self, graphs: dict[str, list[tuple[LibraryGraph, Optional[str]]]], absolute_root_folder: str = '') -> None:
        if not self.use_s3_integration or not self.s3_client or self.s3_setup_failed:
            return
        if not self.bucket or not self.repo_path:
            logging.error(f"Something went wrong: bucket {self.bucket}, repo path {self.repo_path}")
            return
        persist_graphs(graphs, self.s3_client, self.bucket, self.repo_path, self.persist_graphs_timeout,
                       absolute_root_folder=absolute_root_folder)

    def persist_resource_subgraph_maps(self, resource_subgraph_maps: dict[str, dict[str, str]]) -> None:
        if not self.use_s3_integration or not self.s3_client or self.s3_setup_failed:
            return
        if not self.bucket or not self.repo_path:
            logging.error(f"Something went wrong: bucket {self.bucket}, repo path {self.repo_path}")
            return
        persist_resource_subgraph_maps(resource_subgraph_maps, self.s3_client, self.bucket, self.repo_path, self.persist_graphs_timeout)

    def commit_repository(self, branch: str) -> str | None:
        """
        :param branch: branch to be persisted
        Finalize the repository's scanning in bridgecrew's platform.
        """
        try_num = 0
        while try_num < MAX_RETRIES:
            if not self.use_s3_integration or self.s3_setup_failed:
                return None

            request = None
            response = None
            try:
                if not self.http:
                    logging.error("HTTP manager was not correctly created")
                    return None
                if not self.bc_source:
                    logging.error("Source was not set")
                    return None
                if not self.bc_source.upload_results:
                    # no need to upload something
                    return None

                logging.debug(f'Submitting finalize upload request to {self.integrations_api_url}')
                request = self.http.request("PUT", f"{self.integrations_api_url}?source={self.bc_source.name}",  # type:ignore[no-untyped-call]
                                            body=json.dumps(
                                                {"path": self.repo_path, "branch": branch,
                                                 "to_branch": CI_METADATA_EXTRACTOR.to_branch,
                                                 "pr_id": CI_METADATA_EXTRACTOR.pr_id,
                                                 "pr_url": CI_METADATA_EXTRACTOR.pr_url,
                                                 "commit_hash": CI_METADATA_EXTRACTOR.commit_hash,
                                                 "commit_url": CI_METADATA_EXTRACTOR.commit_url,
                                                 "author": CI_METADATA_EXTRACTOR.author_name,
                                                 "author_url": CI_METADATA_EXTRACTOR.author_url,
                                                 "run_id": CI_METADATA_EXTRACTOR.run_id,
                                                 "run_url": CI_METADATA_EXTRACTOR.run_url,
                                                 "repository_url": CI_METADATA_EXTRACTOR.repository_url}),
                                            headers=merge_dicts({"Authorization": self.get_auth_token(),
                                                                 "Content-Type": "application/json",
                                                                 'x-api-client': self.bc_source.name,
                                                                 'x-api-checkov-version': checkov_version},
                                                                get_user_agent_header()
                                                                ))
                response = json.loads(request.data.decode("utf8"))
                logging.debug(f'Request ID: {request.headers.get("x-amzn-requestid")}')
                logging.debug(f'Trace ID: {request.headers.get("x-amzn-trace-id")}')
                url: str = self.get_sso_prismacloud_url(response.get("url", None))
                return url
            except HTTPError:
                logging.error(f"Failed to commit repository {self.repo_path}", exc_info=True)
                self.s3_setup_failed = True
            except JSONDecodeError:
                if request:
                    logging.warning(f"Response (status: {request.status}) of {self.integrations_api_url}: {request.data.decode('utf8')}")  # danger:ignore - we won't be here if the response contains valid data
                logging.error(f"Response of {self.integrations_api_url} is not a valid JSON", exc_info=True)
                self.s3_setup_failed = True
            finally:
                if request and request.status == 201 and response and response.get("result") == "Success":
                    logging.info(f"Finalize repository {self.repo_id} in the platform")
                elif (
                    response
                    and try_num < MAX_RETRIES
                    and re.match("The integration ID .* in progress", response.get("message", ""))
                ):
                    logging.info(
                        f"Failed to persist for repo {self.repo_id}, sleeping for {SLEEP_SECONDS} seconds before retrying")
                    try_num += 1
                    sleep(SLEEP_SECONDS)
                else:
                    logging.error(f"Failed to finalize repository {self.repo_id} in the platform with the following error:\n{response}")
                    self.s3_setup_failed = True

        return None

    def persist_files(self, files_to_persist: list[FileToPersist]) -> None:
        logging.info(f"Persisting {len(files_to_persist)} files")
        with futures.ThreadPoolExecutor() as executor:
            futures.wait(
                [executor.submit(self._persist_file, file_to_persist.full_file_path, file_to_persist.s3_file_key) for
                 file_to_persist in files_to_persist],
                return_when=futures.FIRST_EXCEPTION,
            )
        logging.info(f"Done persisting {len(files_to_persist)} files")

    def _persist_file(self, full_file_path: str, s3_file_key: str) -> None:
        tries = MAX_RETRIES
        curr_try = 0

        if not self.s3_client or not self.bucket or not self.repo_path:
            logging.error(
                f"Something went wrong: S3 client {self.s3_client} bucket {self.bucket}, repo path {self.repo_path}"
            )
            return

        file_object_key = os.path.join(self.repo_path, s3_file_key).replace("\\", "/")
        while curr_try < tries:
            try:
                self.s3_client.upload_file(full_file_path, self.bucket, file_object_key)
                return
            except ClientError as e:
                if e.response.get('Error', {}).get('Code') == 'AccessDenied':
                    sleep(SLEEP_SECONDS)
                    curr_try += 1
                else:
                    logging.error(f"failed to persist file {full_file_path} into S3 bucket {self.bucket}",
                                  exc_info=True)
                    raise
            except Exception:
                logging.error(f"failed to persist file {full_file_path} into S3 bucket {self.bucket}", exc_info=True)
                raise
        if curr_try == tries:
            logging.error(
                f"failed to persist file {full_file_path} into S3 bucket {self.bucket} - gut AccessDenied {tries} times")

    def get_platform_run_config(self) -> None:
        if self.skip_download is True:
            logging.debug("Skipping downloading configs from platform")
            return

        if self.is_integration_configured():
            self.get_customer_run_config()
        else:
            self.get_public_run_config()

    def _get_run_config_query_params(self) -> str:
        return f'module={"bc" if self.is_bc_token(self.bc_api_key) else "pc"}&enforcementv2=true'

    def get_run_config_url(self) -> str:
        return f'{self.platform_run_config_url}?{self._get_run_config_query_params()}'

    def get_customer_run_config(self) -> None:
        if self.skip_download is True:
            logging.debug("Skipping customer run config API call")
            return

        if not self.bc_api_key or not self.is_integration_configured():
            raise Exception(
                "Tried to get customer run config, but the API key was missing or the integration was not set up")

        if not self.bc_source:
            logging.error("Source was not set")
            return

        try:
            token = self.get_auth_token()
            headers = merge_dicts(get_auth_header(token),
                                  get_default_get_headers(self.bc_source, self.bc_source_version))

            self.setup_http_manager()
            if not self.http:
                logging.error("HTTP manager was not correctly created")
                return

            platform_type = PRISMA_PLATFORM if self.is_prisma_integration() else BRIDGECREW_PLATFORM

            url = self.get_run_config_url()
            logging.debug(f'Platform run config URL: {url}')
            request = self.http.request("GET", url, headers=headers)  # type:ignore[no-untyped-call]
            logging.debug(f'Request ID: {request.headers.get("x-amzn-requestid")}')
            logging.debug(f'Trace ID: {request.headers.get("x-amzn-trace-id")}')
            if request.status != 200:
                error_message = get_auth_error_message(request.status, self.is_prisma_integration(), False)
                logging.error(error_message)
                raise BridgecrewAuthError(error_message)
            self.customer_run_config_response = json.loads(request.data.decode("utf8"))

            logging.debug(f"Got customer run config from {platform_type} platform")
        except Exception:
            logging.warning(f"Failed to get the customer run config from {self.platform_run_config_url}", exc_info=True)
            raise

    def get_reachability_run_config(self) -> Union[Dict[str, Any], None]:
        if self.skip_download is True:
            logging.debug("Skipping customer run config API call")
            return None

        if not self.bc_api_key or not self.is_integration_configured():
            raise Exception(
                "Tried to get customer run config, but the API key was missing or the integration was not set up")

        if not self.bc_source:
            logging.error("Source was not set")
            return None

        try:
            token = self.get_auth_token()
            headers = merge_dicts(get_auth_header(token),
                                  get_default_get_headers(self.bc_source, self.bc_source_version))

            self.setup_http_manager()
            if not self.http:
                logging.error("HTTP manager was not correctly created")
                return None

            platform_type = PRISMA_PLATFORM if self.is_prisma_integration() else BRIDGECREW_PLATFORM

            request = self.http.request("GET", self.reachability_run_config_url,
                                        headers=headers)  # type:ignore[no-untyped-call]
            if request.status != 200:
                error_message = get_auth_error_message(request.status, self.is_prisma_integration(), False)
                logging.error(error_message)
                raise BridgecrewAuthError(error_message)

            logging.debug(f"Got reachability run config from {platform_type} platform")

            res: Dict[str, Any] = json.loads(request.data.decode("utf8"))
            return res
        except Exception:
            logging.warning(f"Failed to get the reachability run config from {self.reachability_run_config_url}",
                            exc_info=True)
            raise

    def get_prisma_build_policies(self, policy_filter: str) -> None:
        """
        Get Prisma policy for enriching runConfig with metadata
        Filters: https://prisma.pan.dev/api/cloud/cspm/policy#operation/get-policy-filters-and-options
        :param policy_filter: comma separated filter string. Example, policy.label=A,cloud.type=aws
        :return:
        """
        if self.skip_download is True:
            logging.debug("Skipping prisma policy API call")
            return
        if not policy_filter:
            return
        if not self.is_prisma_integration():
            return
        if not self.bc_api_key or not self.is_integration_configured():
            raise Exception(
                "Tried to get prisma build policy metadata, "
                "but the API key was missing or the integration was not set up")
        try:
            token = self.get_auth_token()
            headers = merge_dicts(get_prisma_auth_header(token), get_prisma_get_headers())

            self.setup_http_manager()
            if not self.http:
                logging.error("HTTP manager was not correctly created")
                return

            logging.debug(f'Prisma policy URL: {self.prisma_policies_url}')
            query_params = convert_prisma_policy_filter_to_dict(policy_filter)
            if self.is_valid_policy_filter(query_params, valid_filters=self.get_prisma_policy_filters()):
                # If enabled and subtype are not explicitly set, use the only acceptable values.
                query_params['policy.enabled'] = True
                query_params['policy.subtype'] = 'build'
                request = self.http.request(  # type:ignore[no-untyped-call]
                    "GET",
                    self.prisma_policies_url,
                    headers=headers,
                    fields=query_params,
                )
                self.prisma_policies_response = json.loads(request.data.decode("utf8"))
                logging.debug("Got Prisma build policy metadata")
            else:
                logging.warning("Skipping get prisma build policies. --policy-metadata-filter will not be applied.")
        except Exception:
            logging.warning(
                f"Failed to get prisma build policy metadata from {self.platform_run_config_url}", exc_info=True)

    def get_prisma_policy_filters(self) -> Dict[str, Dict[str, Any]]:
        try:
            token = self.get_auth_token()
            headers = merge_dicts(get_prisma_auth_header(token), get_prisma_get_headers())

            self.setup_http_manager()
            if not self.http:
                logging.error("HTTP manager was not correctly created")
                return {}

            logging.debug(f'Prisma filter URL: {self.prisma_policy_filters_url}')
            request = self.http.request(  # type:ignore[no-untyped-call]
                "GET",
                self.prisma_policy_filters_url,
                headers=headers,
            )
            policy_filters: dict[str, dict[str, Any]] = json.loads(request.data.decode("utf8"))
            logging.debug(f'Prisma filter suggestion response: {policy_filters}')
            return policy_filters
        except Exception:
            logging.warning(
                f"Failed to get prisma build policy metadata from {self.platform_run_config_url}", exc_info=True)
            return {}

    @staticmethod
    def is_valid_policy_filter(policy_filter: dict[str, str], valid_filters: dict[str, dict[str, Any]] | None = None) -> bool:
        """
        Validates only the filter names
        """
        valid_filters = valid_filters or {}

        if not policy_filter:
            return False
        if not valid_filters:
            return False
        for filter_name, filter_value in policy_filter.items():
            if filter_name not in valid_filters.keys():
                logging.warning(f"Invalid filter name: {filter_name}")
                logging.warning(f"Available filter names: {', '.join(valid_filters.keys())}")
                return False
            elif filter_name == 'policy.subtype' and filter_value != 'build':
                logging.warning(f"Filter value not allowed: {filter_value}")
                logging.warning("Available options: build")
                return False
            elif filter_name == 'policy.enabled' and not convert_str_to_bool(filter_value):
                logging.warning(f"Filter value not allowed: {filter_value}")
                logging.warning("Available options: True")
                return False
        logging.debug("--policy-metadata-filter is valid")
        return True

    def get_public_run_config(self) -> None:
        if self.skip_download is True:
            logging.debug("Skipping checkov mapping and guidelines API call")
            return
        try:
            headers: dict[str, Any] = {}

            self.setup_http_manager()
            if not self.http:
                logging.error("HTTP manager was not correctly created")
                return

            request = self.http.request("GET", self.guidelines_api_url, headers=headers)  # type:ignore[no-untyped-call]
            if request.status >= 300:
                request = self.http.request(  # type:ignore[no-untyped-call]
                    "GET",
                    self.guidelines_api_url_backoff,
                    headers=headers,
                )

            self.public_metadata_response = json.loads(request.data.decode("utf8"))
            platform_type = PRISMA_PLATFORM if self.is_prisma_integration() else BRIDGECREW_PLATFORM
            logging.debug(f"Got checkov mappings and guidelines from {platform_type} platform")
        except Exception:
            logging.warning(f"Failed to get the checkov mappings and guidelines from {self.guidelines_api_url}. Skips using BC_* IDs will not work.",
                            exc_info=True)

    def get_report_to_platform(self, args: argparse.Namespace, scan_reports: list[Report]) -> None:
        if self.bc_api_key:

            if args.directory:
                repo_id = self.get_repository(args)
                self.setup_bridgecrew_credentials(repo_id=repo_id)
            if self.is_integration_configured():
                self._upload_run(args, scan_reports)

    # Added this to generate a default repo_id for cli scans for upload to the platform
    # whilst also persisting a cli repo_id into the object
    def persist_bc_api_key(self, args: argparse.Namespace) -> str | None:
        if args.bc_api_key:
            self.bc_api_key = args.bc_api_key
        else:
            # get the key from file
            self.bc_api_key = read_key()
        return self.bc_api_key

    # Added this to generate a default repo_id for cli scans for upload to the platform
    # whilst also persisting a cli repo_id into the object
    def persist_repo_id(self, args: argparse.Namespace) -> str:
        if args.repo_id is None:
            if CI_METADATA_EXTRACTOR.from_branch:
                self.repo_id = CI_METADATA_EXTRACTOR.from_branch
            if args.directory:
                basename = path.basename(os.path.abspath(args.directory[0]))
                self.repo_id = f"cli_repo/{basename}"
            if args.file:
                # Get the base path of the file based on it's absolute path
                basename = os.path.basename(os.path.dirname(os.path.abspath(args.file[0])))
                self.repo_id = f"cli_repo/{basename}"

        else:
            self.repo_id = args.repo_id

        if not self.repo_id:
            # this should not happen
            self.repo_id = "cli_repo/unknown"

        return self.repo_id

    def get_repository(self, args: argparse.Namespace) -> str:
        if CI_METADATA_EXTRACTOR.from_branch:
            return CI_METADATA_EXTRACTOR.from_branch
        arg_dir = args.directory[0]
        arg_dir.rstrip(os.path.sep)  # If directory ends with /, remove it. Does not remove any other character!!
        basename = 'unnamed_repo' if path.basename(arg_dir) == '.' else path.basename(arg_dir)
        repo_id = f"cli_repo/{basename}"
        return repo_id

    def _upload_run(self, args: argparse.Namespace, scan_reports: list[Report]) -> None:
        print(Style.BRIGHT + colored("Connecting to Bridgecrew.cloud...", 'green',
                                     attrs=['bold']) + Style.RESET_ALL)
        self.persist_repository(args.directory[0])
        print(Style.BRIGHT + colored("Metadata upload complete", 'green',
                                     attrs=['bold']) + Style.RESET_ALL)
        self.persist_scan_results(scan_reports)
        print(Style.BRIGHT + colored("Report upload complete", 'green',
                                     attrs=['bold']) + Style.RESET_ALL)
        self.commit_repository(args.branch)
        print(Style.BRIGHT + colored(
            "COMPLETE! \nYour results are in your Bridgecrew dashboard, available here: https://bridgecrew.cloud \n",
            'green', attrs=['bold']) + Style.RESET_ALL)

    def _input_orgname(self) -> str:
        while True:
            result = str(input('Organization name: ')).lower().strip()  # nosec
            # remove spaces and special characters
            result = ''.join(e for e in result if e.isalnum())
            if result:
                break
        return result

    def _input_visualize_results(self) -> str:
        while True:
            result = str(input('Visualize results? (y/n): ')).lower().strip()  # nosec
            if result[:1] in ["y", "n"]:
                break
        return result

    def _input_levelup_results(self) -> str:
        while True:
            result = str(input('Level up? (y/n): ')).lower().strip()  # nosec
            if result[:1] in ["y", "n"]:
                break
        return result

    def _input_email(self) -> str:
        while True:
            email = str(input('E-Mail: ')).lower().strip()  # nosec
            if re.search(EMAIL_PATTERN, email):
                break
            else:
                print("email should match the following pattern: {}".format(EMAIL_PATTERN))
        return email

    @staticmethod
    def loading_output(msg: str) -> None:
        with trange(ACCOUNT_CREATION_TIME) as t:
            for _ in t:
                t.set_description(msg)
                t.set_postfix(refresh=False)
                sleep(SLEEP_SECONDS)

    def repo_matches(self, repo_name: str) -> bool:
        # matches xyz_org/repo or org/repo (where xyz is the BC org name and the CLI repo prefix from the platform)
        return re.match(re.compile(f'^(\\w+_)?{self.repo_id}$'), repo_name) is not None

    def get_default_headers(self, request_type: str) -> dict[str, Any]:
        if not self.bc_source:
            logging.warning("Source was not set")
            return {}

        if request_type.upper() == "GET":
            return merge_dicts(get_default_get_headers(self.bc_source, self.bc_source_version),
                               {"Authorization": self.get_auth_token()})
        elif request_type.upper() == "POST":
            return merge_dicts(get_default_post_headers(self.bc_source, self.bc_source_version),
                               {"Authorization": self.get_auth_token()})

        logging.info(f"Unsupported request {request_type}")
        return {}

    # Define the function that will get the relay state from the Prisma Cloud Platform.
    def get_sso_prismacloud_url(self, report_url: str) -> str:
        if not bc_integration.prisma_api_url or not self.http or not self.bc_source or report_url is None:
            return report_url or ''
        url_saml_config = f"{bc_integration.prisma_api_url}/saml/config"
        token = self.get_auth_token()
        headers = merge_dicts(get_auth_header(token),
                              get_default_get_headers(self.bc_source, self.bc_source_version))

        request = self.http.request("GET", url_saml_config, headers=headers, timeout=10)  # type:ignore[no-untyped-call]
        if request.status >= 300:
            return report_url

        data = json.loads(request.data.decode("utf8"))

        relay_state_param_name = data.get("relayStateParamName")
        access_saml_url = data.get("redLockAccessSamlUrl")

        if relay_state_param_name and access_saml_url:
            parsed_url = urlparse(report_url)
            uri = parsed_url.path
            # If there are any query parameters, append them to the URI
            if parsed_url.query:
                uri = f"{uri}?{parsed_url.query}"
            # Check if the URL already contains GET parameters.
            if "?" in access_saml_url:
                report_url = f"{access_saml_url}&{relay_state_param_name}={uri}"
            else:
                report_url = f"{access_saml_url}?{relay_state_param_name}={uri}"

        return report_url

    def setup_on_prem(self) -> None:
        if self.customer_run_config_response:
            self.on_prem = self.customer_run_config_response.get('onPrem', False)


bc_integration = BcPlatformIntegration()
