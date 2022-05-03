import json
import logging
import os.path
import re
import webbrowser
from collections import namedtuple
from concurrent import futures
from json import JSONDecodeError
from os import path
from time import sleep
from typing import Optional, List, Dict

import boto3
import dpath.util
import requests
import urllib3
from botocore.exceptions import ClientError
from botocore.config import Config
from cachetools import cached, TTLCache
from colorama import Style
from termcolor import colored
from tqdm import trange
from urllib3.exceptions import HTTPError, MaxRetryError

from checkov.common.bridgecrew.ci_variables import (
    BC_TO_BRANCH,
    BC_PR_ID,
    BC_PR_URL,
    BC_COMMIT_HASH,
    BC_COMMIT_URL,
    BC_AUTHOR_NAME,
    BC_AUTHOR_URL,
    BC_RUN_ID,
    BC_RUN_URL,
    BC_REPOSITORY_URL,
    BC_FROM_BRANCH,
)
from checkov.common.bridgecrew.platform_errors import BridgecrewAuthError
from checkov.common.bridgecrew.platform_key import read_key, persist_key, bridgecrew_file
from checkov.common.bridgecrew.wrapper import reduce_scan_reports, persist_checks_results, \
    enrich_and_persist_checks_metadata, checkov_results_prefix, _put_json_object
from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS, SUPPORTED_FILES
from checkov.common.output.report import CheckType
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.http_utils import normalize_prisma_url, get_auth_header, get_default_get_headers, \
    get_user_agent_header, get_default_post_headers
from checkov.version import version as checkov_version

SLEEP_SECONDS = 1

EMAIL_PATTERN = re.compile(r"[^@]+@[^@]+\.[^@]+")
UUID_V4_PATTERN = re.compile(r"^[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}$")

ACCOUNT_CREATION_TIME = 180  # in seconds

UNAUTHORIZED_MESSAGE = 'User is not authorized to access this resource with an explicit deny'
ASSUME_ROLE_UNUATHORIZED_MESSAGE = 'is not authorized to perform: sts:AssumeRole'

FileToPersist = namedtuple('FileToPersist', 'full_file_path s3_file_key')

DEFAULT_REGION = "us-west-2"
MAX_RETRIES = 40
ONBOARDING_SOURCE = "checkov"

SIGNUP_HEADER = merge_dicts({
    'Accept': 'application/json',
    'Content-Type': 'application/json;charset=UTF-8'},
    get_user_agent_header())


class BcPlatformIntegration(object):
    def __init__(self):
        self.bc_api_key = read_key()
        self.s3_client = None
        self.bucket = None
        self.credentials = None
        self.repo_path = None
        self.repo_id = None
        self.repo_branch = None
        self.skip_fixes = False
        self.skip_download = False
        self.bc_source = None
        self.bc_source_version = None
        self.timestamp = None
        self.scan_reports = []
        self.bc_api_url = os.getenv('BC_API_URL', "https://www.bridgecrew.cloud")
        self.prisma_api_url = normalize_prisma_url(os.getenv("PRISMA_API_URL"))
        self.setup_api_urls()
        self.customer_run_config_response = None
        self.public_metadata_response = None
        self.use_s3_integration = False
        self.platform_integration_configured = False
        self.http = None
        self.bc_skip_mapping = False
        self.cicd_details = {}

    def setup_api_urls(self):
        """
        API URLs vary depending upon whether the platform is Bridgecrew or Prisma Cloud.
        Bridgecrew has one default that can be used when initializing the class,
        but Prisma Cloud requires resetting them in setup_bridgecrew_credentials,
        which is where command-line parameters are first made available.
        """
        if self.prisma_api_url:
            self.api_url = f"{self.prisma_api_url}/bridgecrew"
        else:
            self.api_url = self.bc_api_url
        self.guidelines_api_url = f"{self.api_url}/api/v1/guidelines"
        self.integrations_api_url = f"{self.api_url}/api/v1/integrations/types/checkov"
        self.onboarding_url = f"{self.api_url}/api/v1/signup/checkov"
        self.platform_run_config_url = f"{self.api_url}/api/v1/checkov/runConfiguration"

    def is_prisma_integration(self) -> bool:
        return self.bc_api_key and not self.is_bc_token(self.bc_api_key)

    @staticmethod
    def is_bc_token(token: str) -> bool:
        return re.match(UUID_V4_PATTERN, token) is not None

    @cached(TTLCache(maxsize=1, ttl=540))
    def get_auth_token(self) -> str:
        if self.is_bc_token(self.bc_api_key):
            return self.bc_api_key
        # A Prisma Cloud Access Key was specified as the Bridgecrew token.
        if not self.prisma_api_url:
            raise ValueError("A Prisma Cloud token was set, but no Prisma Cloud API URL was set")
        if '::' not in self.bc_api_key:
            raise ValueError("A Prisma Cloud token was set, but the token is not in the correct format: <access_key_id>::<secret_key>")
        username, password = self.bc_api_key.split('::')
        request = self.http.request("POST", f"{self.prisma_api_url}/login",
                                    body=json.dumps({"username": username, "password": password}),
                                    headers=merge_dicts({"Content-Type": "application/json"}, get_user_agent_header()))
        if request.status == 401:
            raise BridgecrewAuthError()
        token = json.loads(request.data.decode("utf8"))['token']
        return token

    def setup_http_manager(self, ca_certificate=os.getenv('BC_CA_BUNDLE', None)):
        """
        bridgecrew uses both the urllib3 and requests libraries, while checkov uses the requests library.
        :param ca_certificate: an optional CA bundle to be used by both libraries.
        """
        if self.http:
            return
        if ca_certificate:
            os.environ['REQUESTS_CA_BUNDLE'] = ca_certificate
            try:
                self.http = urllib3.ProxyManager(os.environ['https_proxy'], cert_reqs='REQUIRED', ca_certs=ca_certificate)
            except KeyError:
                self.http = urllib3.PoolManager(cert_reqs='REQUIRED', ca_certs=ca_certificate)
        else:
            try:
                self.http = urllib3.ProxyManager(os.environ['https_proxy'])
            except KeyError:
                self.http = urllib3.PoolManager()

    def setup_bridgecrew_credentials(self, repo_id, skip_fixes=False, skip_download=False, source=None,
                                     source_version=None, repo_branch=None, prisma_api_url=None):
        """
        Setup credentials against Bridgecrew's platform.
        :param repo_id: Identity string of the scanned repository, of the form <repo_owner>/<repo_name>
        :param skip_fixes: whether to skip querying fixes from Bridgecrew
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

        if self.bc_source.upload_results:
            try:
                self.skip_fixes = True  # no need to run fixes on CI integration
                repo_full_path, response = self.get_s3_role(repo_id)
                self.bucket, self.repo_path = repo_full_path.split("/", 1)
                self.timestamp = self.repo_path.split("/")[-1]
                self.credentials = response["creds"]
                config = Config(
                    s3={
                        "use_accelerate_endpoint": True,
                    }
                )
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=self.credentials["AccessKeyId"],
                    aws_secret_access_key=self.credentials["SecretAccessKey"],
                    aws_session_token=self.credentials["SessionToken"],
                    region_name=DEFAULT_REGION,
                    config=config,
                )
                self.platform_integration_configured = True
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

        self.platform_integration_configured = True

    def get_s3_role(self, repo_id):
        token = self.get_auth_token()
        request = self.http.request("POST", self.integrations_api_url, body=json.dumps({"repoId": repo_id}),
                                    headers=merge_dicts({"Authorization": token, "Content-Type": "application/json"},
                                                        get_user_agent_header()))
        if request.status == 403:
            raise BridgecrewAuthError()
        response = json.loads(request.data.decode("utf8"))
        while ('Message' in response or 'message' in response):
            if 'Message' in response and response['Message'] == UNAUTHORIZED_MESSAGE:
                raise BridgecrewAuthError()
            if 'message' in response and ASSUME_ROLE_UNUATHORIZED_MESSAGE in response['message']:
                raise BridgecrewAuthError("Checkov got an unexpected authorization error that may not be due to your credentials. Please contact support.")
            if 'message' in response and "cannot be found" in response['message']:
                self.loading_output("creating role")
                request = self.http.request("POST", self.integrations_api_url, body=json.dumps({"repoId": repo_id}),
                                            headers=merge_dicts(
                                                {"Authorization": token, "Content-Type": "application/json"},
                                                get_user_agent_header()))
                response = json.loads(request.data.decode("utf8"))

        repo_full_path = response["path"]
        return repo_full_path, response

    def is_integration_configured(self):
        """
        Checks if Bridgecrew integration is fully configured based in input params.
        :return: True if the integration is configured, False otherwise
        """
        return self.platform_integration_configured

    def persist_repository(self, root_dir, files=None, excluded_paths=None, included_paths: Optional[List[str]] = None):
        """
        Persist the repository found on root_dir path to Bridgecrew's platform. If --file flag is used, only files
        that are specified will be persisted.
        :param files: Absolute path of the files passed in the --file flag.
        :param root_dir: Absolute path of the directory containing the repository root level.
        :param excluded_paths: Paths to exclude from persist process
        :param included_paths: Paths to exclude from persist process
        """
        excluded_paths = excluded_paths if excluded_paths is not None else []

        if not self.use_s3_integration:
            return
        files_to_persist: List[FileToPersist] = []
        if files:
            for f in files:
                f_name = os.path.basename(f)
                _, file_extension = os.path.splitext(f)
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
                    if file_extension in SUPPORTED_FILE_EXTENSIONS or file_path in SUPPORTED_FILES:
                        full_file_path = os.path.join(root_path, file_path)
                        relative_file_path = os.path.relpath(full_file_path, root_dir)
                        files_to_persist.append(FileToPersist(full_file_path, relative_file_path))

        self.persist_files(files_to_persist)

    def persist_git_configuration(self, root_dir, git_config_folders: List[str]):
        if not self.use_s3_integration:
            return
        files_to_persist: List[FileToPersist] = []

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

    def persist_scan_results(self, scan_reports):
        """
        Persist checkov's scan result into bridgecrew's platform.
        :param scan_reports: List of checkov scan reports
        """
        if not self.use_s3_integration:
            return

        self.scan_reports = scan_reports
        reduced_scan_reports = reduce_scan_reports(scan_reports)
        checks_metadata_paths = enrich_and_persist_checks_metadata(scan_reports, self.s3_client, self.bucket,
                                                                   self.repo_path)
        dpath.util.merge(reduced_scan_reports, checks_metadata_paths)
        persist_checks_results(reduced_scan_reports, self.s3_client, self.bucket, self.repo_path)

    def persist_image_scan_results(self, report: Dict[str, any], file_path: str, image_name: str, branch: str) -> None:
        target_report_path = f'{self.repo_path}/{checkov_results_prefix}/{CheckType.SCA_IMAGE}/raw_results.json'
        to_upload = {"report": report, "file_path": file_path, "image_name": image_name, "branch": branch}
        _put_json_object(self.s3_client, to_upload, self.bucket, target_report_path)

    def commit_repository(self, branch):
        """
        :param branch: branch to be persisted
        Finalize the repository's scanning in bridgecrew's platform.
        """
        try_num = 0
        while try_num < MAX_RETRIES:
            if not self.use_s3_integration:
                return

            request = None
            response = None
            try:

                request = self.http.request("PUT", f"{self.integrations_api_url}?source={self.bc_source.name}",
                                            body=json.dumps(
                                                {"path": self.repo_path, "branch": branch, "to_branch": BC_TO_BRANCH,
                                                 "pr_id": BC_PR_ID, "pr_url": BC_PR_URL,
                                                 "commit_hash": BC_COMMIT_HASH, "commit_url": BC_COMMIT_URL,
                                                 "author": BC_AUTHOR_NAME, "author_url": BC_AUTHOR_URL,
                                                 "run_id": BC_RUN_ID, "run_url": BC_RUN_URL,
                                                 "repository_url": BC_REPOSITORY_URL}),
                                            headers=merge_dicts({"Authorization": self.get_auth_token(),
                                                                 "Content-Type": "application/json",
                                                                 'x-api-client': self.bc_source.name,
                                                                 'x-api-checkov-version': checkov_version},
                                                                get_user_agent_header()
                                                                ))
                response = json.loads(request.data.decode("utf8"))
                url = response.get("url", None)
                return url
            except HTTPError:
                logging.error(f"Failed to commit repository {self.repo_path}", exc_info=True)
                raise
            except JSONDecodeError:
                logging.error(f"Response of {self.integrations_api_url} is not a valid JSON", exc_info=True)
                raise
            finally:
                if request.status == 201 and response and response.get("result") == "Success":
                    logging.info(f"Finalize repository {self.repo_id} in bridgecrew's platform")
                elif try_num < MAX_RETRIES and re.match('The integration ID .* in progress',
                                                        response.get('message', '')):
                    logging.info(f"Failed to persist for repo {self.repo_id}, sleeping for {SLEEP_SECONDS} seconds before retrying")
                    try_num += 1
                    sleep(SLEEP_SECONDS)
                else:
                    raise Exception(
                        f"Failed to finalize repository {self.repo_id} in bridgecrew's platform\n{response}")

    def persist_files(self, files_to_persist: List[FileToPersist]):
        logging.info(f"Persisting {len(files_to_persist)} files")
        with futures.ThreadPoolExecutor() as executor:
            futures.wait(
                [executor.submit(self._persist_file, file_to_persist.full_file_path, file_to_persist.s3_file_key) for
                 file_to_persist in files_to_persist],
                return_when=futures.FIRST_EXCEPTION,
            )
        logging.info(f"Done persisting {len(files_to_persist)} files")

    def _persist_file(self, full_file_path, s3_file_key):
        tries = MAX_RETRIES
        curr_try = 0
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
                    raise
            except Exception:
                logging.error(f"failed to persist file {full_file_path} into S3 bucket {self.bucket}", exc_info=True)
                raise
        if curr_try == tries:
            logging.error(
                f"failed to persist file {full_file_path} into S3 bucket {self.bucket} - gut AccessDenied {tries} times")

    def get_platform_run_config(self):
        if self.skip_download is True:
            logging.debug("Skipping downloading configs from platform")
            return

        if self.is_integration_configured():
            self.get_customer_run_config()
        else:
            self.get_public_run_config()

    def get_run_config_url(self):
        return f'{self.platform_run_config_url}?module={"bc" if self.is_bc_token(self.bc_api_key) else "pc"}'

    def get_customer_run_config(self) -> None:
        if self.skip_download is True:
            logging.debug("Skipping customer run config API call")
            return

        if not self.bc_api_key or not self.is_integration_configured():
            raise Exception("Tried to get customer run config, but the API key was missing or the integration was not set up")

        try:
            token = self.get_auth_token()
            headers = merge_dicts(get_auth_header(token), get_default_get_headers(self.bc_source, self.bc_source_version))
            if not self.http:
                self.setup_http_manager()
            url = self.get_run_config_url()
            logging.debug(f'Platform run config URL: {url}')
            request = self.http.request("GET", url, headers=headers)
            self.customer_run_config_response = json.loads(request.data.decode("utf8"))
            logging.debug("Got customer run config from Bridgecrew BE")
        except Exception:
            logging.warning(f"Failed to get the customer run config from {self.platform_run_config_url}", exc_info=True)

    def get_public_run_config(self) -> None:
        if self.skip_download is True:
            logging.debug("Skipping checkov mapping and guidelines API call")
            return

        try:
            headers = {}
            if not self.http:
                self.setup_http_manager()
            request = self.http.request("GET", self.guidelines_api_url, headers=headers)
            self.public_metadata_response = json.loads(request.data.decode("utf8"))
            logging.debug("Got checkov mappings and guidelines from Bridgecrew BE")
        except Exception:
            logging.warning(f"Failed to get the checkov mappings and guidelines from {self.guidelines_api_url}", exc_info=True)

    def onboarding(self):
        if not self.bc_api_key:
            print(Style.BRIGHT + colored("\nWould you like to “level up” your Checkov powers for free?  The upgrade includes: \n\n", 'green',
                                         attrs=['bold']) + colored(
                u"\u2022 " + "Command line docker Image scanning\n"
                             u"\u2022 " + "Software Composition Analysis\n"
                                          u"\u2022 " + "Centralized policy management\n"
                                                       u"\u2022 " + "Free bridgecrew.cloud account with API access\n"
                u"\u2022 " + "Auto-fix remediation suggestions\n"
                u"\u2022 " + "Enabling of VS Code Plugin\n"
                u"\u2022 " + "Dashboard visualisation of Checkov scans\n"
                u"\u2022 " + "Integration with GitHub for:\n"
                "\t" + u"\u25E6 " + "\tAutomated Pull Request scanning\n"
                "\t" + u"\u25E6 " + "\tAuto remediation PR generation\n"
                u"\u2022 " + "Integration with up to 100 cloud resources for:\n"
                "\t" + u"\u25E6 " + "\tAutomated cloud resource checks\n"
                "\t" + u"\u25E6 " + "\tResource drift detection\n"
                "\n"           
                "\n" + "and much more...",'yellow') +
                colored("\n\nIt's easy and only takes 2 minutes. We can do it right now!\n\n"
                "To Level-up, press 'y'... \n",
                'cyan') + Style.RESET_ALL)
            reply = self._input_levelup_results()
            if reply[:1] == 'y':
                print(Style.BRIGHT + colored("\nOk, let’s get you started on creating your free account! \n"
                "\nEnter your email address to begin: ",'green', attrs=['bold']) + colored(" // This will be used as your login at https://bridgecrew.cloud.\n", 'green'))
                if not self.bc_api_key:
                    email = self._input_email()
                    print(Style.BRIGHT + colored("\nLooks good!"
                    "\nNow choose an Organisation Name: ",'green', attrs=['bold']) + colored(" // This will enable collaboration with others who you can add to your team.\n", 'green'))
                    org = self._input_orgname()
                    print(Style.BRIGHT + colored("\nAmazing!"
                    "\nWe are now generating a personal API key to immediately enable some new features… ",'green', attrs=['bold']))

                    bc_api_token, response = self.get_api_token(email, org)
                    self.bc_api_key = bc_api_token
                    if response.status_code == 200:
                        print(Style.BRIGHT + colored("\nComplete!", 'green', attrs=['bold']))
                        print('\nSaving API key to {}'.format(bridgecrew_file))
                        print(Style.BRIGHT + colored("\nCheckov will automatically check this location for a key.  If you forget it you’ll find it here\nhttps://bridgecrew.cloud/integrations/api-token\n\n",'green'))
                        persist_key(self.bc_api_key)
                        print(Style.BRIGHT + colored("Checkov Dashboard is configured, opening https://bridgecrew.cloud to explore your new powers.", 'green', attrs=['bold']))
                        print(Style.BRIGHT + colored("FYI - check your inbox for login details! \n", 'green'))

                        print(Style.BRIGHT + colored("Congratulations! You’ve just super-sized your Checkov!  Why not test-drive image scanning now:",'cyan'))

                        print(Style.BRIGHT + colored("\ncheckov --docker-image ubuntu --dockerfile-path /Users/bob/workspaces/bridgecrew/Dockerfile --repo-id bob/test --branch master\n",'white'))

                        print(Style.BRIGHT + colored("Or download our VS Code plugin:  https://github.com/bridgecrewio/checkov-vscode \n", 'cyan',attrs=['bold']))

                        print(Style.BRIGHT + colored("Interested in contributing to Checkov as an open source developer.  We thought you’d never ask.  Check us out at: \nhttps://github.com/bridgecrewio/checkov/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22 \n", 'white', attrs=['bold']))

                    else:
                        print(
                            Style.BRIGHT + colored("\nCould not create account, please try again on your next scan! \n",
                                                   'red', attrs=['bold']) + Style.RESET_ALL)
                    webbrowser.open(
                        "https://bridgecrew.cloud/?utm_source=cli&utm_medium=organic_oss&utm_campaign=checkov")
            else:
                print(
                    "\n To see the Dashboard prompt again, run `checkov` with no arguments \n For Checkov usage, try `checkov --help`")
        else:
            print("No argument given. Try ` --help` for further information")

    def get_report_to_platform(self, args, scan_reports):
        if self.bc_api_key:

            if args.directory:
                repo_id = self.get_repository(args)
                self.setup_bridgecrew_credentials(repo_id=repo_id)
            if self.is_integration_configured():
                self._upload_run(args, scan_reports)

    # Added this to generate a default repo_id for cli scans for upload to the platform
    # whilst also persisting a cli repo_id into the object
    def persist_bc_api_key(self, args):
        if args.bc_api_key:
            self.bc_api_key = args.bc_api_key
        else:
            # get the key from file
            self.bc_api_key = read_key()
        return self.bc_api_key

    # Added this to generate a default repo_id for cli scans for upload to the platform
    # whilst also persisting a cli repo_id into the object
    def persist_repo_id(self, args):
        if args.repo_id is None:
            if BC_FROM_BRANCH:
                self.repo_id = BC_FROM_BRANCH
            if args.directory:
                basename = path.basename(os.path.abspath(args.directory[0]))
                self.repo_id = "cli_repo/" + basename
            if args.file:
                # Get the base path of the file based on it's absolute path
                basename = os.path.basename(os.path.dirname(os.path.abspath(args.file[0])))
                self.repo_id = "cli_repo/" + basename

        else:
            self.repo_id = args.repo_id
        return self.repo_id

    def get_repository(self, args):
        if BC_FROM_BRANCH:
            return BC_FROM_BRANCH
        basename = 'unnamed_repo' if path.basename(args.directory[0]) == '.' else path.basename(args.directory[0])
        repo_id = "cli_repo/" + basename
        return repo_id

    def get_api_token(self, email, org):
        response = self._create_bridgecrew_account(email, org)
        bc_api_token = response.json()["checkovSignup"]
        return bc_api_token, response

    def _upload_run(self, args, scan_reports):
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
            "COMPLETE! \nYour results are in your Bridgecrew dashboard, available here: https://bridgecrew.cloud \n", 'green', attrs=['bold']) + Style.RESET_ALL)

    def _create_bridgecrew_account(self, email, org):
        """
        Create new bridgecrew account
        :param email: email of account owner
        :return: account creation response
        """
        payload = {
            "owner_email": email,
            "org": org,
            "source": ONBOARDING_SOURCE,
            "customer_name": org
        }
        response = requests.request("POST", self.onboarding_url, headers=SIGNUP_HEADER, json=payload)
        if response.status_code == 200:
            return response
        else:
            raise Exception("failed to create a bridgecrew account. An organization with this name might already "
                            "exist with this email address. Please login bridgecrew.cloud to retrieve access key")

    def _input_orgname(self):
        valid = False
        result = None
        while not valid:
            result = str(
                input(
                    'Organization name: ')).lower().strip()  # nosec
            # remove spaces and special characters
            result = ''.join(e for e in result if e.isalnum())
            if result:
                valid = True
        return result

    def _input_visualize_results(self):
        valid = False
        result = None
        while not valid:
            result = str(input('Visualize results? (y/n): ')).lower().strip()  # nosec
            if result[:1] in ["y", "n"]:
                valid = True
        return result

    def _input_levelup_results(self):
        valid = False
        result = None
        while not valid:
            result = str(input('Level up? (y/n): ')).lower().strip()  # nosec
            if result[:1] in ["y", "n"]:
                valid = True
        return result

    def _input_email(self):
        valid_email = False
        email = ''
        while not valid_email:
            email = str(input('E-Mail: ')).lower().strip()  # nosec
            if re.search(EMAIL_PATTERN, email):
                valid_email = True
            else:
                print("email should match the following pattern: {}".format(EMAIL_PATTERN))
        return email

    @staticmethod
    def loading_output(msg):
        with trange(ACCOUNT_CREATION_TIME) as t:
            for _ in t:
                t.set_description(msg)
                t.set_postfix(refresh=False)
                sleep(SLEEP_SECONDS)

    def repo_matches(self, repo_name):
        # matches xyz_org/repo or org/repo (where xyz is the BC org name and the CLI repo prefix from the platform)
        return re.match(re.compile(f'^(\\w+_)?{self.repo_id}$'), repo_name) is not None

    def get_default_headers(self, request_type: str) -> dict:
        if request_type.upper() == "GET":
            return merge_dicts(get_default_get_headers(self.bc_source, self.bc_source_version),
                               {"Authorization": self.get_auth_token()})
        elif request_type.upper() == "POST":
            return merge_dicts(get_default_post_headers(self.bc_source, self.bc_source_version),
                               {"Authorization": self.get_auth_token()})

        logging.info(f"Unsupported request {request_type}")
        return {}


bc_integration = BcPlatformIntegration()
