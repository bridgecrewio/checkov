from __future__ import annotations

import asyncio
import json
import logging
import os.path
import re
import sys
import uuid
from collections import namedtuple
from concurrent import futures
from io import StringIO
from json import JSONDecodeError
from os import path
from pathlib import Path
from time import sleep
from types import MethodType
from typing import List, Dict, TYPE_CHECKING, Any, Set, cast, Optional, Union
from urllib.parse import urlparse

import boto3
import dpath
import urllib3
import urllib.parse
from botocore.config import Config
from botocore.exceptions import ClientError
from cachetools import cached, TTLCache
from colorama import Style
from termcolor import colored
from tqdm import trange
from urllib3.exceptions import HTTPError, MaxRetryError

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.platform_errors import BridgecrewAuthError, PlatformConnectionError
from checkov.common.bridgecrew.platform_key import read_key
from checkov.common.bridgecrew.run_metadata.registry import registry
from checkov.common.bridgecrew.wrapper import persist_assets_results, reduce_scan_reports, \
    persist_checks_results, \
    enrich_and_persist_checks_metadata, checkov_results_prefix, persist_run_metadata, _put_json_object, \
    persist_graphs, persist_resource_subgraph_maps, persist_reachability_results, \
    persist_multiple_logs_stream
from checkov.common.models.consts import SAST_SUPPORTED_FILE_EXTENSIONS, SUPPORTED_FILE_EXTENSIONS, SUPPORTED_FILES, SCANNABLE_PACKAGE_FILES
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.common.sast.consts import SastLanguages, CDK_FRAMEWORK_PREFIX
from checkov.common.typing import _CicdDetails, LibraryGraph
from checkov.common.util.consts import PRISMA_PLATFORM, BRIDGECREW_PLATFORM
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
from checkov.common.util.type_forcers import convert_prisma_policy_filter_to_params, convert_str_to_bool
from checkov.version import version as checkov_version

if TYPE_CHECKING:
    import argparse
    from checkov.common.bridgecrew.bc_source import SourceType
    from checkov.common.output.report import Report
    from checkov.secrets.coordinator import EnrichedSecret
    from mypy_boto3_s3.client import S3Client
    from typing_extensions import TypeGuard
    from checkov.common.sast.report_types import Match, SkippedCheck

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
PRISMA_GOV_API_URL = 'https://api.gov.prismacloud.io'
JAKARTA_API_URL = 'https://api.id.prismacloud.io'

API_URL_REGION_MAP = {
    PRISMA_GOV_API_URL: 'us-gov-west-1',
    JAKARTA_API_URL: 'ap-southeast-3'
}

REGIONS_URL_NOT_SUPPORT_S3_ACCELERATE = {
    PRISMA_GOV_API_URL,
    JAKARTA_API_URL
}

MAX_RETRIES = 40

CI_METADATA_EXTRACTOR = registry.get_extractor()

REQUEST_STATUS_CODES_RETRY = [401, 408, 500, 502, 503, 504]
REQUEST_METHODS_TO_RETRY = ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'PUT', 'TRACE', 'POST']


class BcPlatformIntegration:
    def __init__(self) -> None:
        self.clean()
        self.set_config()

    def clean(self) -> None:
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
        self.bc_api_url = normalize_bc_url(os.getenv('BC_API_URL'))
        self.prisma_api_url = normalize_prisma_url(os.getenv('PRISMA_API_URL') or 'https://api0.prismacloud.io')
        self.prisma_policies_url: str | None = None
        self.prisma_policy_filters_url: str | None = None
        self.custom_auth_headers: dict[str, str] = {}
        self.custom_auth_token: str | None = None
        self.setup_api_urls()
        self.customer_run_config_response = None
        self.runtime_run_config_response = None
        self.prisma_policies_response: dict[str, str] | None = None
        self.prisma_policies_exception_response: dict[str, str] | None = None
        self.public_metadata_response = None
        self.use_s3_integration = False
        self.s3_setup_failed = False
        self.platform_integration_configured = False
        self.http: urllib3.PoolManager | urllib3.ProxyManager | None = None
        self.http_timeout = urllib3.Timeout(connect=REQUEST_CONNECT_TIMEOUT, read=REQUEST_READ_TIMEOUT)
        self.http_retry = urllib3.Retry(
            REQUEST_RETRIES,
            redirect=3,
            status_forcelist=REQUEST_STATUS_CODES_RETRY,
            allowed_methods=REQUEST_METHODS_TO_RETRY
        )
        self.bc_skip_mapping = False
        self.cicd_details: _CicdDetails = {}
        self.support_flag_enabled = False
        self.enable_persist_graphs = convert_str_to_bool(os.getenv('BC_ENABLE_PERSIST_GRAPHS', 'True'))
        self.persist_graphs_timeout = int(os.getenv('BC_PERSIST_GRAPHS_TIMEOUT', 60))
        self.ca_certificate: str | None = None
        self.no_cert_verify: bool = False
        self.on_prem: bool = False
        self.daemon_process = False  # set to 'True' when running in multiprocessing 'spawn' mode
        self.scan_dir: List[str] = []
        self.scan_file: List[str] = []
        self.sast_custom_policies: str = ''

    def init_instance(self, platform_integration_data: dict[str, Any]) -> None:
        """This is mainly used for recreating the instance without interacting with the platform again"""

        self.daemon_process = True

        self.bc_api_url = platform_integration_data["bc_api_url"]
        self.bc_api_key = platform_integration_data["bc_api_key"]
        self.bc_source = platform_integration_data["bc_source"]
        self.bc_source_version = platform_integration_data["bc_source_version"]
        self.bucket = platform_integration_data["bucket"]
        self.cicd_details = platform_integration_data["cicd_details"]
        self.credentials = platform_integration_data["credentials"]
        self.platform_integration_configured = platform_integration_data["platform_integration_configured"]
        self.prisma_api_url = platform_integration_data.get("prisma_api_url", 'https://api0.prismacloud.io')
        self.custom_auth_headers = platform_integration_data["custom_auth_headers"]
        self.custom_auth_token = platform_integration_data["custom_auth_token"]
        self.repo_branch = platform_integration_data["repo_branch"]
        self.repo_id = platform_integration_data["repo_id"]
        self.repo_path = platform_integration_data["repo_path"]
        self.skip_fixes = platform_integration_data["skip_fixes"]
        self.timestamp = platform_integration_data["timestamp"]
        self.use_s3_integration = platform_integration_data["use_s3_integration"]
        self.setup_api_urls()
        # 'mypy' doesn't like, when you try to override an instance method
        self.get_auth_token = MethodType(lambda _=None: platform_integration_data["get_auth_token"], self)  # type:ignore[method-assign]

    def generate_instance_data(self) -> dict[str, Any]:
        """This output is used to re-initialize the instance and should be kept in sync with 'init_instance()'"""

        return {
            # 'api_url' will be set by invoking 'setup_api_urls()'
            "bc_api_url": self.bc_api_url,
            "bc_api_key": self.bc_api_key,
            "bc_source": self.bc_source,
            "bc_source_version": self.bc_source_version,
            "bucket": self.bucket,
            "cicd_details": self.cicd_details,
            "credentials": self.credentials,
            "platform_integration_configured": self.platform_integration_configured,
            "prisma_api_url": self.prisma_api_url,
            "custom_auth_headers": self.custom_auth_headers,
            "repo_branch": self.repo_branch,
            "repo_id": self.repo_id,
            "repo_path": self.repo_path,
            "skip_fixes": self.skip_fixes,
            "timestamp": self.timestamp,
            "use_s3_integration": self.use_s3_integration,
            # will be overriden with a simple lambda expression
            "get_auth_token": self.get_auth_token() if self.bc_api_key else ""
        }

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
        if self.bc_api_url:
            self.api_url = self.bc_api_url
        else:
            self.api_url = f"{self.prisma_api_url}/bridgecrew"
            self.prisma_policies_url = f"{self.prisma_api_url}/v2/policy"
            self.prisma_policy_filters_url = f"{self.prisma_api_url}/filter/policy/suggest"
        self.guidelines_api_url = f"{self.api_url}/api/v2/guidelines"
        self.guidelines_api_url_backoff = f"{self.api_url}/api/v1/guidelines"

        self.integrations_api_url = f"{self.api_url}/api/v1/integrations/types/checkov"
        self.platform_run_config_url = f"{self.api_url}/api/v2/checkov/runConfiguration"
        self.reachability_run_config_url = f"{self.api_url}/api/v2/checkov/reachabilityRunConfiguration"
        self.runtime_run_config_url = f"{self.api_url}/api/v1/runtime-images/repositories"

    def is_prisma_integration(self) -> bool:
        if (self.bc_api_key and not self.is_bc_token(self.bc_api_key)) or self.custom_auth_token:
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
        if self.custom_auth_token:
            return self.custom_auth_token
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

    @staticmethod
    def set_config() -> None:
        # asyncio - on windows aiodns needs SelectorEventLoop
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    def setup_bridgecrew_credentials(
        self,
        repo_id: str,
        skip_download: bool = False,
        source: SourceType | None = None,
        skip_fixes: bool = False,
        source_version: str | None = None,
        repo_branch: str | None = None,
        prisma_api_url: str | None = None,
        bc_api_url: str | None = None
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

        if bc_api_url:
            self.prisma_api_url = None
            self.bc_api_url = normalize_bc_url(bc_api_url)
            self.setup_api_urls()
            logging.info(f'Using BC API URL: {self.bc_api_url}')

        if prisma_api_url:
            self.prisma_api_url = normalize_prisma_url(prisma_api_url)
            self.setup_api_urls()
            logging.info(f'Using Prisma API URL: {self.prisma_api_url}')

        if self.bc_source and self.bc_source.upload_results:
            self.set_s3_integration()

        self.platform_integration_configured = True

    def _get_source_id_from_repo_path(self, repo_path: str) -> str | None:
        repo_path_parts = repo_path.split("/")
        if not repo_path_parts and repo_path_parts[0] != 'checkov':
            logging.error(f'failed to get source_id from repo_path. repo_path format is unknown: ${repo_path}')
            return None
        try:
            return '/'.join(repo_path_parts[2:4])
        except IndexError:
            logging.error(f'failed to get source_id from repo_path. repo_path format is unknown: ${repo_path}')
            return None

    def set_s3_integration(self) -> None:
        try:
            self.skip_fixes = True  # no need to run fixes on CI integration
            repo_full_path, support_path, response = self.get_s3_role(self.repo_id)  # type: ignore
            if not repo_full_path:  # happens if the setup fails with something other than an auth error - we continue locally
                return

            self.bucket, self.repo_path = repo_full_path.split("/", 1)
            self.source_id = self._get_source_id_from_repo_path(self.repo_path)
            self.timestamp = self.repo_path.split("/")[-2]
            self.credentials = cast("dict[str, str]", response["creds"])

            self.set_s3_client()

            if self.support_flag_enabled:
                self.support_bucket, self.support_repo_path = cast(str, support_path).split("/", 1)

            self.use_s3_integration = True
            self.platform_integration_configured = True
        except MaxRetryError as e:
            # almost all failures should be caught by this block - we need to differentiate what actually happened
            # for the causes that are almost certainly user error, we want to hide the exception details
            # so that it does not look like checkov crashed due to a bug (stack traces are scary for users)
            if str(e.reason) == 'too many 401 error responses':
                logging.error('An authentication error occurred connecting to the platform after multiple retries. '
                              'Please verify that your API key and Prisma API URL are correct, and retry.')
            elif isinstance(e.reason, urllib3.exceptions.SSLError):
                logging.error("An SSL error occurred connecting to the platform. If you are on a VPN, please try "
                              f"disabling it and re-running the command. The error is: {e.reason}")
            else:
                logging.error('An error occurred connecting to the platform after multiple retries. Please verify your '
                              'API key and Prisma API URL, as well as network connectivity, and retry. If the problem '
                              'persists, please enable debug logs and contact support.')
            logging.debug('The exception details:', exc_info=True)
            raise PlatformConnectionError(str(e.reason)) from e
        except HTTPError as e:
            logging.error('An unexpected error occurred connecting to the platform. Please verify your '
                          'API key and Prisma API URL, as well as network connectivity, and retry. If the problem '
                          'persists, please enable debug logs and contact support.', exc_info=True)
            raise PlatformConnectionError(str(e)) from e
        except JSONDecodeError as e:
            logging.error('An unexpected error occurred processing the response from the platform. Please verify your '
                          'API key and Prisma API URL, as well as network connectivity, and retry. If the problem '
                          'persists, please enable debug logs and contact support.', exc_info=True)
            raise PlatformConnectionError(str(e)) from e
        except BridgecrewAuthError:
            logging.error('An authentication error occurred connecting to the platform after multiple retries. '
                          'Please verify that your API keys and Prisma API URL are correct, and retry.')
            raise

    def set_s3_client(self) -> None:
        if not self.credentials:
            raise ValueError("Credentials for client are not set")

        region = DEFAULT_REGION
        use_accelerate_endpoint = True

        if self.prisma_api_url in REGIONS_URL_NOT_SUPPORT_S3_ACCELERATE:
            use_accelerate_endpoint = False
            region = API_URL_REGION_MAP[self.prisma_api_url]

        try:
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
        except ClientError:
            logging.error(f"Failed to initiate client with credentials {self.credentials}", exc_info=True)
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
                                                        get_user_agent_header(),
                                                        self.custom_auth_headers))
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
        sast_languages: Set[SastLanguages] | None = None
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
                if file_extension in SCANNABLE_PACKAGE_FILES:
                    continue
                if file_extension in SUPPORTED_FILE_EXTENSIONS or f_name in SUPPORTED_FILES:
                    files_to_persist.append(FileToPersist(f, os.path.relpath(f, root_dir)))
                if sast_languages:
                    for framwork in sast_languages:
                        if file_extension in SAST_SUPPORTED_FILE_EXTENSIONS[framwork]:
                            files_to_persist.append(FileToPersist(f, os.path.relpath(f, root_dir)))
                            break

        else:
            for root_path, d_names, f_names in os.walk(root_dir):
                # self.excluded_paths only contains the config fetched from the platform.
                # but here we expect the list from runner_registry as well (which includes self.excluded_paths).
                filter_ignored_paths(root_path, d_names, excluded_paths, included_paths=included_paths)
                filter_ignored_paths(root_path, f_names, excluded_paths)
                for file_path in f_names:
                    _, file_extension = os.path.splitext(file_path)
                    if file_extension in SCANNABLE_PACKAGE_FILES:
                        continue
                    full_file_path = os.path.join(root_path, file_path)
                    relative_file_path = os.path.relpath(full_file_path, root_dir)
                    if file_extension in SUPPORTED_FILE_EXTENSIONS or file_path in SUPPORTED_FILES or is_dockerfile(file_path):
                        files_to_persist.append(FileToPersist(full_file_path, relative_file_path))
                    if sast_languages:
                        for framwork in sast_languages:
                            if file_extension in SAST_SUPPORTED_FILE_EXTENSIONS[framwork]:
                                files_to_persist.append(FileToPersist(full_file_path, relative_file_path))
                                break

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

    def adjust_sast_match_location_path(self, match: Match) -> None:
        for dir in self.scan_dir:
            if match.location.path.startswith(os.path.abspath(dir)):
                match.location.path = match.location.path.replace(os.path.abspath(dir), self.repo_path)  # type: ignore
                if match.metadata.code_locations:
                    for code_location in match.metadata.code_locations:
                        code_location.path = code_location.path.replace(os.path.abspath(dir), self.repo_path)  # type: ignore

                if match.metadata.taint_mode and match.metadata.taint_mode.data_flow:
                    for df in match.metadata.taint_mode.data_flow:
                        df.path = df.path.replace(os.path.abspath(dir), self.repo_path)  # type: ignore

                return

        for file in self.scan_file:
            if match.location.path == os.path.abspath(file):
                file_dir = '/'.join(match.location.path.split('/')[0:-1])
                match.location.path = match.location.path.replace(os.path.abspath(file_dir), self.repo_path)  # type: ignore
                if match.metadata.code_locations:
                    for code_location in match.metadata.code_locations:
                        code_location.path = code_location.path.replace(os.path.abspath(file_dir), self.repo_path)  # type: ignore

                if match.metadata.taint_mode and match.metadata.taint_mode.data_flow:
                    for df in match.metadata.taint_mode.data_flow:
                        df.path = df.path.replace(os.path.abspath(file_dir), self.repo_path)  # type: ignore

                return

    def adjust_sast_skipped_checks_path(self, skipped_checks_by_file: Dict[str, List[SkippedCheck]]) -> None:
        for filepath in list(skipped_checks_by_file.keys()):
            new_filepath = None
            for dir in self.scan_dir:
                if filepath.startswith(os.path.abspath(dir)):
                    file_dir = '/'.join(filepath.split('/')[0:-1])
                    new_filepath = filepath.replace(os.path.abspath(file_dir), self.repo_path)  # type: ignore
                    break
            for file in self.scan_file:
                if filepath == os.path.abspath(file):
                    file_dir = '/'.join(filepath.split('/')[0:-1])
                    new_filepath = filepath.replace(os.path.abspath(file_dir), self.repo_path)  # type: ignore
                    break
            if new_filepath:
                skipped_checks_by_file[new_filepath] = skipped_checks_by_file[filepath]
                skipped_checks_by_file.pop(filepath)

    @staticmethod
    def _delete_code_block_from_sast_report(report: Dict[str, Any]) -> None:
        if isinstance(report, dict):
            for key, value in report.items():
                if key == 'code_block':
                    report[key] = ''
                BcPlatformIntegration._delete_code_block_from_sast_report(value)
        if isinstance(report, list):
            for item in report:
                BcPlatformIntegration._delete_code_block_from_sast_report(item)

    @staticmethod
    def save_sast_report_locally(sast_scan_reports: Dict[str, Dict[str, Any]]) -> None:
        for lang, report in sast_scan_reports.items():
            filename = f'{lang}_report.json'
            with open(f"/tmp/{filename}", 'w') as f:  # nosec
                f.write(json.dumps(report))

    def persist_sast_scan_results(self, reports: List[Report]) -> None:
        sast_scan_reports = {}
        for report in reports:
            if not report.check_type.lower().startswith(CheckType.SAST):
                continue
            if not hasattr(report, 'sast_report') or not report.sast_report:
                continue
            for _, match_by_check in report.sast_report.rule_match.items():
                for _, match in match_by_check.items():
                    for m in match.matches:
                        self.adjust_sast_match_location_path(m)
                self.adjust_sast_skipped_checks_path(report.sast_report.skipped_checks_by_file)

                sast_scan_reports[report.check_type] = report.sast_report.model_dump(mode='json')
            if self.on_prem:
                BcPlatformIntegration._delete_code_block_from_sast_report(sast_scan_reports)

        if os.getenv('SAVE_SAST_REPORT_LOCALLY'):
            self.save_sast_report_locally(sast_scan_reports)

        persist_checks_results(sast_scan_reports, self.s3_client, self.bucket, self.repo_path)  # type: ignore

    def persist_cdk_scan_results(self, reports: List[Report]) -> None:
        cdk_scan_reports = {}
        for report in reports:
            if not report.check_type.startswith(CDK_FRAMEWORK_PREFIX):
                continue
            if not report.cdk_report:  # type: ignore
                continue
            for match_by_check in report.cdk_report.rule_match.values():  # type: ignore
                for _, match in match_by_check.items():
                    for m in match.matches:
                        self.adjust_sast_match_location_path(m)
                cdk_scan_reports[report.check_type] = report.cdk_report.model_dump(mode='json')  # type: ignore
            if self.on_prem:
                BcPlatformIntegration._delete_code_block_from_sast_report(cdk_scan_reports)

        # In case we dont have sast report - create empty one
        sast_reports = {}
        for check_type, report in cdk_scan_reports.items():
            lang = check_type.split('_')[1]
            found_sast_report = False
            for report in reports:
                if report.check_type == f'sast_{lang}':
                    found_sast_report = True
            if not found_sast_report:
                sast_reports[f'sast_{lang}'] = report.empty_sast_report.model_dump(mode='json')  # type: ignore

        persist_checks_results(sast_reports, self.s3_client, self.bucket, self.repo_path)  # type: ignore
        persist_checks_results(cdk_scan_reports, self.s3_client, self.bucket, self.repo_path)  # type: ignore

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
        if self.support_bucket and self.support_repo_path:
            logging.debug(f'Also uploading run_metadata.json to support location: {self.support_bucket}/{self.support_repo_path}')
            persist_run_metadata(run_metadata, self.s3_client, self.support_bucket, self.support_repo_path, False)

    def persist_all_logs_streams(self, logs_streams: Dict[str, StringIO]) -> None:
        if not self.use_s3_integration or not self.s3_client or self.s3_setup_failed:
            return
        if not self.support_bucket or not self.support_repo_path:
            logging.error(
                f"Something went wrong with the log upload location: bucket {self.support_bucket}, repo path {self.support_repo_path}")
            return

        persist_multiple_logs_stream(logs_streams, self.s3_client, self.support_bucket, self.support_repo_path)

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
                                                                get_user_agent_header(),
                                                                self.custom_auth_headers
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
                    logging.error(f"failed to persist file {full_file_path} into S3 bucket {self.bucket}", exc_info=True)
                    logging.debug(f"file size of {full_file_path} is {os.stat(full_file_path).st_size} bytes")
                    raise
            except Exception:
                logging.error(f"failed to persist file {full_file_path} into S3 bucket {self.bucket}", exc_info=True)
                logging.debug(f"file size of {full_file_path} is {os.stat(full_file_path).st_size} bytes")
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
        # ignore mypy warning that this can be null
        return f'module={"bc" if self.is_bc_token(self.bc_api_key) else "pc"}&enforcementv2=true&repoId={urllib.parse.quote(self.repo_id)}'  # type: ignore

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
                                  get_default_get_headers(self.bc_source, self.bc_source_version),
                                  self.custom_auth_headers)

            self.setup_http_manager()
            if not self.http:
                logging.error("HTTP manager was not correctly created")
                return

            platform_type = PRISMA_PLATFORM if self.is_prisma_integration() else BRIDGECREW_PLATFORM

            url = self.get_run_config_url()
            logging.debug(f'Platform run config URL: {url}')
            request = self.http.request("GET", url, headers=headers)  # type:ignore[no-untyped-call]
            request_id = request.headers.get("x-amzn-requestid")
            trace_id = request.headers.get("x-amzn-trace-id")
            logging.debug(f'Request ID: {request_id}')
            logging.debug(f'Trace ID: {trace_id}')
            if request.status == 500:
                error_message = 'An unexpected backend error occurred getting the run configuration from the platform (status code 500). ' \
                                'please contact support and provide debug logs and the values below. You may be able to use the --skip-download option ' \
                                'to bypass this error, but this will prevent platform configurations (e.g., custom policies, suppressions) from ' \
                                f'being used in the scan.\nRequest ID: {request_id}\nTrace ID: {trace_id}'
                logging.error(error_message)
                raise Exception(error_message)
            elif request.status != 200:
                error_message = get_auth_error_message(request.status, self.is_prisma_integration(), False)
                logging.error(error_message)
                raise BridgecrewAuthError(error_message)
            self.customer_run_config_response = json.loads(request.data.decode("utf8"))

            logging.debug(f"Got customer run config from {platform_type} platform")
        except Exception as e:
            logging.warning(f"An unexpected error occurred getting the run configuration from {self.platform_run_config_url} "
                            "after multiple retries. Please verify your API key and Prisma API URL, and retry. If the "
                            "problem persists, please enable debug logs and contact support. The error is: "
                            f"{e}", exc_info=True)
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
                                  get_default_get_headers(self.bc_source, self.bc_source_version),
                                  self.custom_auth_headers)

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

    def get_runtime_run_config(self) -> None:
        try:
            if self.skip_download is True:
                logging.debug("Skipping customer run config API call")
                raise

            if not self.bc_api_key or not self.is_integration_configured():
                raise Exception(
                    "Tried to get customer run config, but the API key was missing or the integration was not set up")

            if not self.bc_source:
                logging.error("Source was not set")
                raise

            token = self.get_auth_token()
            headers = merge_dicts(get_auth_header(token),
                                  get_default_get_headers(self.bc_source, self.bc_source_version),
                                  self.custom_auth_headers)

            self.setup_http_manager()
            if not self.http:
                logging.error("HTTP manager was not correctly created")
                raise

            platform_type = PRISMA_PLATFORM if self.is_prisma_integration() else BRIDGECREW_PLATFORM
            url = f"{self.runtime_run_config_url}?repoId={self.repo_id}"
            request = self.http.request("GET", url,
                                        headers=headers)  # type:ignore[no-untyped-call]
            if request.status != 200:
                error_message = get_auth_error_message(request.status, self.is_prisma_integration(), False)
                logging.error(error_message)
                raise BridgecrewAuthError(error_message)

            logging.debug(f"Got run config from {platform_type} platform")

            self.runtime_run_config_response = json.loads(request.data.decode("utf8"))
        except Exception:
            logging.debug('could not get runtime info for this repo')

    def get_prisma_build_policies(self, policy_filter: str, policy_filter_exception: str) -> None:
        """
        Get Prisma policy for enriching runConfig with metadata
        Filters: https://prisma.pan.dev/api/cloud/cspm/policy#operation/get-policy-filters-and-options
        :param policy_filter: comma separated filter string. Example, policy.label=A,cloud.type=aws
        :param policy_filter_exception: comma separated filter string. Example, policy.label=A,cloud.type=aws
        :return:
        """
        if self.skip_download is True:
            logging.debug("Skipping prisma policy API call")
            return
        if not policy_filter and not policy_filter_exception:
            return
        if not self.is_prisma_integration():
            return
        if not self.bc_api_key or not self.is_integration_configured():
            raise Exception(
                "Tried to get prisma build policy metadata, "
                "but the API key was missing or the integration was not set up")
        self.prisma_policies_response = self.get_prisma_policies_for_filter(policy_filter)
        self.prisma_policies_exception_response = self.get_prisma_policies_for_filter(policy_filter_exception)

    def get_prisma_policies_for_filter(self, policy_filter: str) -> dict[Any, Any] | None:
        request = None
        filtered_policies = None
        try:
            token = self.get_auth_token()
            headers = merge_dicts(get_prisma_auth_header(token), get_prisma_get_headers(), self.custom_auth_headers)

            self.setup_http_manager()
            if not self.http:
                logging.error("HTTP manager was not correctly created")
                return filtered_policies

            logging.debug(f'Prisma policy URL: {self.prisma_policies_url}')
            query_params = convert_prisma_policy_filter_to_params(policy_filter)
            if self.is_valid_policy_filter(query_params, valid_filters=self.get_prisma_policy_filters()):
                # If enabled and subtype are not explicitly set, use the only acceptable values.
                self.add_static_policy_filters(query_params)
                logging.debug(f'Filter query params: {query_params}')

                request = self.http.request(  # type:ignore[no-untyped-call]
                    "GET",
                    self.prisma_policies_url,
                    headers=headers,
                    fields=tuple(query_params),
                )
                logging.debug("Got Prisma build policy metadata")
                filtered_policies = json.loads(request.data.decode("utf8"))
        except Exception:
            response_message = f': {request.status} - {request.reason}' if request else ''
            logging.warning(
                f"Failed to get prisma build policy metadata from {self.prisma_policies_url}{response_message}", exc_info=True)
        return filtered_policies

    @staticmethod
    def add_static_policy_filters(query_params: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """
        Adds policy.enabled = true, policy.subtype = build to the query params, if these are not already present. Modifies the list in place and also returns it.
        """
        if not any(p[0] == 'policy.enabled' for p in query_params):
            query_params.append(('policy.enabled', 'true'))
        if not any(p[0] == 'policy.subtype' for p in query_params):
            query_params.append(('policy.subtype', 'build'))
        return query_params

    def get_prisma_policy_filters(self) -> Dict[str, Dict[str, Any]]:
        request = None
        try:
            token = self.get_auth_token()
            headers = merge_dicts(get_prisma_auth_header(token), get_prisma_get_headers(), self.custom_auth_headers)

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
            response_message = f': {request.status} - {request.reason}' if request else ''
            logging.warning(
                f"Failed to get prisma build policy metadata from {self.prisma_policy_filters_url}{response_message}", exc_info=True)
            return {}

    @staticmethod
    def is_valid_policy_filter(policy_filter: list[tuple[str, str]], valid_filters: dict[str, dict[str, Any]] | None = None) -> bool:
        """
        Validates only the filter names
        """
        valid_filters = valid_filters or {}

        if not policy_filter:
            return False
        if not valid_filters:
            return False
        for filter_name, filter_value in policy_filter:
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
        logging.debug("policy filter is valid")
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
        print(Style.BRIGHT + colored("Connecting to Prisma Cloud...", 'green',
                                     attrs=['bold']) + Style.RESET_ALL)
        self.persist_repository(args.directory[0])
        print(Style.BRIGHT + colored("Metadata upload complete", 'green',
                                     attrs=['bold']) + Style.RESET_ALL)
        self.persist_scan_results(scan_reports)
        self.persist_sast_scan_results(scan_reports)
        self.persist_cdk_scan_results(scan_reports)
        print(Style.BRIGHT + colored("Report upload complete", 'green',
                                     attrs=['bold']) + Style.RESET_ALL)
        self.commit_repository(args.branch)
        print(Style.BRIGHT + colored(
            "COMPLETE! \nYour results are in your Prisma Cloud account \n",
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
                               {"Authorization": self.get_auth_token()},
                               self.custom_auth_headers)
        elif request_type.upper() == "POST":
            return merge_dicts(get_default_post_headers(self.bc_source, self.bc_source_version),
                               {"Authorization": self.get_auth_token()},
                               self.custom_auth_headers)

        logging.info(f"Unsupported request {request_type}")
        return {}

    # Define the function that will get the relay state from the Prisma Cloud Platform.
    def get_sso_prismacloud_url(self, report_url: str) -> str:
        if not bc_integration.prisma_api_url or not self.http or not self.bc_source or report_url is None:
            return report_url or ''
        url_saml_config = f"{bc_integration.prisma_api_url}/saml/config"
        token = self.get_auth_token()
        headers = merge_dicts(get_auth_header(token),
                              get_default_get_headers(self.bc_source, self.bc_source_version),
                              bc_integration.custom_auth_headers)

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

                # First encoding
                encoded_uri = urllib.parse.quote(uri)

                # Second encoding
                uri = urllib.parse.quote(encoded_uri)
            # Check if the URL already contains GET parameters.
            if "?" in access_saml_url:
                report_url = f"{access_saml_url}&{relay_state_param_name}={uri}"
            else:
                report_url = f"{access_saml_url}?{relay_state_param_name}={uri}"

        return report_url

    def setup_on_prem(self) -> None:
        if self.customer_run_config_response:
            self.on_prem = self.customer_run_config_response.get('tenantConfig', {}).get('preventCodeUploads', False)
            if self.on_prem:
                logging.debug('On prem mode is enabled')


bc_integration = BcPlatformIntegration()
