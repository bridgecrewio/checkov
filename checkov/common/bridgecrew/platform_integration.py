import sys
from time import sleep

import boto3
import dpath.util
import json
import logging
import os
import re
import requests
import urllib3
from botocore.exceptions import ClientError
from colorama import Style
from git import Repo
from json import JSONDecodeError
from os import path
from termcolor import colored
from tqdm import trange
from urllib3.exceptions import HTTPError

from checkov.common.bridgecrew.platform_errors import BridgecrewAuthError
from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS
from .wrapper import reduce_scan_reports, persist_checks_results, enrich_and_persist_checks_metadata

ACCOUNT_CREATION_TIME = 180  # in seconds

UNAUTHORIZED_MESSAGE = 'User is not authorized to access this resource with an explicit deny'

DEFAULT_REGION = "us-west-2"

ONBOARDING_SOURCE = "checkov"

signupHeaders = {
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8'
}

try:
    http = urllib3.ProxyManager(os.environ['https_proxy'])
except KeyError:
    http = urllib3.PoolManager()


class BcPlatformIntegration(object):
    def __init__(self):
        self.bc_api_key = None
        self.s3_client = None
        self.bucket = None
        self.credentials = None
        self.repo_path = None
        self.repo_id = None
        self.timestamp = None
        self.scan_reports = []
        self.bc_api_url = os.getenv('BC_API_URL', "https://www.bridgecrew.cloud/api/v1")
        self.bc_source = os.getenv('BC_SOURCE', "cli")
        self.integrations_api_url = f"{self.bc_api_url}/integrations/types/checkov"
        self.guidelines_api_url = f"{self.bc_api_url}/guidelines"
        self.onboarding_url = f"{self.bc_api_url}/signup/checkov"

    def setup_bridgecrew_credentials(self, bc_api_key, repo_id):
        """
        Setup credentials against Bridgecrew's platform.
        :param repo_id: Identity string of the scanned repository, of the form <repo_owner>/<repo_name>
        :param bc_api_key: Bridgecrew issued API key
        """
        self.bc_api_key = bc_api_key
        self.repo_id = repo_id
        try:
            request = http.request("POST", self.integrations_api_url, body=json.dumps({"repoId": repo_id}),
                                   headers={"Authorization": bc_api_key, "Content-Type": "application/json"})
            response = json.loads(request.data.decode("utf8"))
            if 'Message' in response:
                if response['Message'] == UNAUTHORIZED_MESSAGE:
                    raise BridgecrewAuthError()
            repo_full_path = response["path"]
            self.bucket, self.repo_path = repo_full_path.split("/", 1)
            self.timestamp = self.repo_path.split("/")[-1]
            self.credentials = response["creds"]
            self.s3_client = boto3.client("s3",
                                          aws_access_key_id=self.credentials["AccessKeyId"],
                                          aws_secret_access_key=self.credentials["SecretAccessKey"],
                                          aws_session_token=self.credentials["SessionToken"],
                                          region_name=DEFAULT_REGION
                                          )
            sleep(10)  # Wait for the policy to update
        except HTTPError as e:
            logging.error(f"Failed to get customer assumed role\n{e}")
            raise e
        except ClientError as e:
            logging.error(f"Failed to initiate client with credentials {self.credentials}\n{e}")
            raise e
        except JSONDecodeError as e:
            logging.error(f"Response of {self.integrations_api_url} is not a valid JSON\n{e}")
            raise e

    def is_integration_configured(self):
        """
        Checks if Bridgecrew integration is fully configured.
        :return: True if the integration is configured, False otherwise
        """
        return all([self.repo_path, self.credentials, self.s3_client])

    def persist_repository(self, root_dir):
        """
        Persist the repository found on root_dir path to Bridgecrew's platform
        :param root_dir: Absolute path of the directory containing the repository root level
        """
        for root_path, d_names, f_names in os.walk(root_dir):
            for file_path in f_names:
                _, file_extension = os.path.splitext(file_path)
                if file_extension in SUPPORTED_FILE_EXTENSIONS:
                    full_file_path = os.path.join(root_path, file_path)
                    relative_file_path = os.path.relpath(full_file_path, root_dir)
                    self._persist_file(full_file_path, relative_file_path)

    def persist_scan_results(self, scan_reports):
        """
        Persist checkov's scan result into bridgecrew's platform.
        :param scan_reports: List of checkov scan reports
        """
        self.scan_reports = scan_reports
        reduced_scan_reports = reduce_scan_reports(scan_reports)
        checks_metadata_paths = enrich_and_persist_checks_metadata(scan_reports, self.s3_client, self.bucket,
                                                                   self.repo_path)
        dpath.util.merge(reduced_scan_reports, checks_metadata_paths)
        persist_checks_results(reduced_scan_reports, self.s3_client, self.bucket, self.repo_path)

    def commit_repository(self, branch):
        """
        :param branch: branch to be persisted
        Finalize the repository's scanning in bridgecrew's platform.
        """
        request = None
        try:
            request = http.request("PUT", f"{self.integrations_api_url}?source={self.bc_source}",
                                   body=json.dumps({"path": self.repo_path, "branch": branch}),
                                   headers={"Authorization": self.bc_api_key, "Content-Type": "application/json"})
            response = json.loads(request.data.decode("utf8"))
        except HTTPError as e:
            logging.error(f"Failed to commit repository {self.repo_path}\n{e}")
            raise e
        except JSONDecodeError as e:
            logging.error(f"Response of {self.integrations_api_url} is not a valid JSON\n{e}")
            raise e
        finally:
            if request.status == 201 and response["result"] == "Success":
                logging.info(f"Finalize repository {self.repo_id} in bridgecrew's platform")
            else:
                raise Exception(f"Failed to finalize repository {self.repo_id} in bridgecrew's platform\n{response}")

    def _persist_file(self, full_file_path, relative_file_path):
        tries = 4
        curr_try = 0
        file_object_key = os.path.join(self.repo_path, relative_file_path)
        while curr_try < tries:
            try:
                self.s3_client.upload_file(full_file_path, self.bucket, file_object_key)
                return
            except ClientError as e:
                if e.response.get('Error', {}).get('Code') == 'AccessDenied':
                    sleep(5)
                    curr_try += 1
                else:
                    logging.error(f"failed to persist file {full_file_path} into S3 bucket {self.bucket}\n{e}")
                    raise e
            except Exception as e:
                logging.error(f"failed to persist file {full_file_path} into S3 bucket {self.bucket}\n{e}")
                raise e
        if curr_try == tries:
            logging.error(
                f"failed to persist file {full_file_path} into S3 bucket {self.bucket} - gut AccessDenied {tries} times")

    def get_guidelines(self) -> dict:
        try:
            request = http.request("GET", self.guidelines_api_url)
            response = json.loads(request.data.decode("utf8"))
            guidelines_map = response["guidelines"]
            logging.debug(f"Got guidelines form Bridgecrew BE")
            return guidelines_map
        except Exception as e:
            logging.debug(f"Failed to get the guidelines from {self.guidelines_api_url}, error:\n{e}")
            return {}

    def onboarding(self, args, scan_reports):
        if os.isatty(sys.stdout.fileno()):
            print(Style.BRIGHT + colored("Visualize and collaborate on these issues with Bridgecrew! \n", 'blue',
                                         attrs=['bold']) + colored(
                "Bridgecrew's dashboard for Checkov allows automation of future checks, Pull Request scanning and "
                "auto-comments, automatic remidiation PR's and more! Plus it's free for 100 Terraform objects and a "
                "great way to visualize and collaborate on these Checkov results. To instantly see this scan in the "
                "platform, Press y! \n ",
                'yellow') + Style.RESET_ALL)
            reply = str(input('Visualize results? (y/n): ')).lower().strip()
            if reply[:1] == 'y':
                print(Style.BRIGHT + colored("\nEmail Address? \n", 'blue', attrs=['bold']) + colored(
                    "Last prompt, promise, well automate the rest, and redirect you to your visualizations! ",
                    'yellow') + Style.RESET_ALL)
                email = str(input('E-Mail:')).lower().strip()
                org = str(
                    input('Organization name (this will create an account with matching identifier): ')).lower().strip()

                response = self._create_bridgecrew_account(email, org)

                # DONE: Integrate with lambda for user creation
                if response.status_code == 200:

                    bc_api_token = response.json()["userApiToken"]
                    print(Style.BRIGHT + colored("Account Created! \n", 'green', attrs=['bold']) + Style.RESET_ALL)
                    print(Style.BRIGHT + colored("Using API Token: {} \n".format(bc_api_token), 'green',
                                                 attrs=['bold']) + Style.RESET_ALL)

                    if args.directory:
                        valid_repos = 0
                        # Work out git repo name for BC --repo-id from root_folder
                        for dir in args.directory:
                            try:
                                repo = Repo(dir)
                                git_remote_uri = repo.remotes.origin.url
                                git_repo_dict = re.match(r'(https|git)(:\/\/|@)([^\/:]+)[\/:]([^\/:]+)\/(.+).git',
                                                         git_remote_uri).group(4, 5)
                                repo_id = git_repo_dict[0] + "/" + git_repo_dict[1]
                                valid_repos += 1
                            except:
                                pass
                        if valid_repos == 0:
                            repo_id = "cli_repo/" + path.basename(args.directory[0])

                    self.setup_bridgecrew_credentials(bc_api_key=bc_api_token, repo_id=repo_id)
                    if self.is_integration_configured():
                        self._upload_run(args, response, scan_reports)

                else:
                    print(Style.BRIGHT + colored("\nCould not create account, please try again on your next scan! \n",
                                                 'red', attrs=['bold']) + Style.RESET_ALL)

    def _upload_run(self, args, response, scan_reports):
        print(Style.BRIGHT + colored("Sucessfully configured Bridgecrew.cloud...", 'green',
                                     attrs=['bold']) + Style.RESET_ALL)
        self.persist_repository(args.directory[0])
        print(Style.BRIGHT + colored("Metadata upload complete", 'green',
                                     attrs=['bold']) + Style.RESET_ALL)
        self.persist_scan_results(scan_reports)
        print(Style.BRIGHT + colored("Checkov report upload complete", 'green',
                                     attrs=['bold']) + Style.RESET_ALL)
        self.commit_repository(args.branch)
        print(Style.BRIGHT + colored(
            "COMPLETE! Your Bridgecrew dashboard is available here: \n {} \n Username: {} \n Pasword: {}".format(
                response.json()["dashboardURL"], response.json()["userEmail"],
                response.json()["userPassword"]), 'blue', attrs=['bold']) + Style.RESET_ALL)

    def _create_bridgecrew_account(self, email, org):
        """
        Create new bridgecrew account
        :param email: email of account owner
        :return: account creation response
        """
        payload = {
            "email": email,
            "org": org,
            "source": ONBOARDING_SOURCE
        }
        response = requests.request("POST", self.onboarding_url, headers=signupHeaders, json=payload)
        with trange(ACCOUNT_CREATION_TIME) as t:
            for _ in t:
                t.set_description('Creating Bridgecrew account & configuring Checkov')
                t.set_postfix(refresh=False)
                sleep(0.1)

        return response
