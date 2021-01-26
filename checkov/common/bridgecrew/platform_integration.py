from itertools import groupby
from time import sleep

import json
import logging
import os
import re
import requests
import urllib3
import webbrowser
from colorama import Style
from os import path
from termcolor import colored
from tqdm import trange
from checkov.common.bridgecrew.platform_key import read_key, persist_key, bridgecrew_file


EMAIL_PATTERN = "[^@]+@[^@]+\.[^@]+"

ACCOUNT_CREATION_TIME = 180  # in seconds

UNAUTHORIZED_MESSAGE = 'User is not authorized to access this resource with an explicit deny'

DEFAULT_REGION = "us-west-2"

ONBOARDING_SOURCE = "checkov"

SIGNUP_HEADER = {
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
        self.bc_api_key = read_key()
        self.s3_client = None
        self.bucket = None
        self.credentials = None
        self.repo_path = None
        self.repo_id = None
        self.branch = None
        self.skip_fixes = False
        self.skip_suppressions = False
        self.timestamp = None
        self.scan_reports = []
        self.bc_api_url = os.getenv('BC_API_URL', "https://www.bridgecrew.cloud/api/v1")
        self.bc_source = os.getenv('BC_SOURCE', 'cli')
        self.bc_source_version = None
        self.integrations_api_url = f"{self.bc_api_url}/integrations/types/checkov"
        self.guidelines_api_url = f"{self.bc_api_url}/guidelines"
        self.onboarding_url = f"{self.bc_api_url}/signup/checkov"
        self.api_token_url = f"{self.bc_api_url}/integrations/apiToken"
        self.suppressions_url = f"{self.bc_api_url}/suppressions"
        self.fixes_url = f"{self.bc_api_url}/fixes/checkov"
        self.root_folder = None
        self.guidelines = None
        self.bc_id_mapping = None
        self.ckv_to_bc_id_mapping = None
        self.use_s3_integration = False
        self.platform_integration_configured = False

    def setup_bridgecrew_credentials(self, bc_api_key, repo_id, branch=None, skip_fixes=False, skip_suppressions=False, source=None, source_version=None):
        """
        Setup credentials against Bridgecrew's platform.
        :param skip_fixes: whether to skip querying fixes from Bridgecrew
        :param repo_id: Identity string of the scanned repository, of the form <repo_owner>/<repo_name>
        :param bc_api_key: Bridgecrew issued API key
        """
        self.bc_api_key = bc_api_key
        self.repo_id = repo_id
        if branch:
            self.branch = branch
        self.skip_fixes = skip_fixes
        self.skip_suppressions = skip_suppressions
        if source:
            self.bc_source = source
        if source_version:
            self.bc_source_version = source_version
        self.get_id_mapping()
        self.platform_integration_configured = True

    def is_integration_configured(self):
        """
        Checks if Bridgecrew integration is fully configured based in input params.
        :return: True if the integration is configured, False otherwise
        """
        return self.platform_integration_configured

    def get_guidelines(self) -> dict:
        if not self.guidelines:
            self.get_checkov_mapping_metadata()
        return self.guidelines

    def get_id_mapping(self) -> dict:
        if not self.bc_id_mapping:
            self.get_checkov_mapping_metadata()
        return self.bc_id_mapping

    def get_ckv_to_bc_id_mapping(self) -> dict:
        if not self.ckv_to_bc_id_mapping:
            self.get_checkov_mapping_metadata()
        return self.ckv_to_bc_id_mapping

    def get_checkov_mapping_metadata(self) -> dict:
        try:
            request = http.request("GET", self.guidelines_api_url)
            response = json.loads(request.data.decode("utf8"))
            self.guidelines = response["guidelines"]
            self.bc_id_mapping = response.get("idMapping")
            self.ckv_to_bc_id_mapping = {ckv_id: bc_id for (bc_id, ckv_id) in self.bc_id_mapping.items()}
            logging.debug(f"Got checkov mappings from Bridgecrew BE")
        except Exception as e:
            logging.debug(f"Failed to get the guidelines from {self.guidelines_api_url}, error:\n{e}")
            return {}

    def onboarding(self):
        if not self.bc_api_key:
            print(Style.BRIGHT + colored("Visualize and collaborate on security issues with Bridgecrew! \n", 'blue',
                                         attrs=['bold']) + colored(
                "Bridgecrew's dashboard allows automation of future checks, Pull Request scanning and "
                "auto-comments, automatic remidiation PR's and more! \n Plus it's free for 100 cloud resources and a "
                "great way to visualize and collaborate on Checkov results. For more information on dashboard integration, see: http://bridge.dev/checkov-dashboard \n \n To instantly see future Checkov scans in the "
                "platform, Press y! \n",
                'yellow') + Style.RESET_ALL)
            reply = self._input_visualize_results()
            if reply[:1] == 'y':
                print(Style.BRIGHT + colored("\nEmail Address? \n", 'blue', attrs=['bold']))
                if not self.bc_api_key:
                    email = self._input_email()
                    org = self._input_orgname()

                    bc_api_token, response = self.get_api_token(email, org)
                    self.bc_api_key = bc_api_token
                    if response.status_code == 200:
                        print('\n Saving API key to {}'.format(bridgecrew_file))
                        print(Style.BRIGHT + colored("\n Checkov Dashboard configured, opening https://bridgecrew.cloud, check your inbox for login details! \n", 'blue', attrs=['bold']))
                        persist_key(self.bc_api_key)
                    else:
                        print(
                            Style.BRIGHT + colored("\nCould not create account, please try again on your next scan! \n",
                                                   'red', attrs=['bold']) + Style.RESET_ALL)
                    webbrowser.open("https://bridgecrew.cloud/?utm_source=cli&utm_medium=organic_oss&utm_campaign=checkov")
            else:
                print("\n To see the Dashboard prompt again, run `checkov` with no arguments \n For Checkov usage, try `checkov --help`")
        else:
            print("No argument given. Try ` --help` for further information")

    # def get_report_to_platform(self, args, scan_reports):
    #     if self.bc_api_key:
    #         if args.directory:
    #             repo_id = self.get_repository(args)
    #             self.setup_bridgecrew_credentials(bc_api_key=self.bc_api_key, repo_id=repo_id)
    #         if self.is_integration_configured():
    #             self._upload_run(args, scan_reports)

    def get_repository(self, args):
        repo_id = "cli_repo/" + path.basename(args.directory[0])
        valid_repos = 0
        # Work out git repo name for BC --repo-id from root_folder
        # for dir in args.directory:
        #     try:
        #         repo = Repo(dir)
        #         git_remote_uri = repo.remotes.origin.url
        #         git_repo_dict = re.match(r'(https|git)(:\/\/|@)([^\/:]+)[\/:]([^\/:]+)\/(.+).git',
        #                                  git_remote_uri).group(4, 5)
        #         repo_id = git_repo_dict[0] + "/" + git_repo_dict[1]
        #         valid_repos += 1
        #     except:  # nosec
        #         pass
        return repo_id

    def get_api_token(self, email, org):
        response = self._create_bridgecrew_account(email, org)
        bc_api_token = response.json()["checkovSignup"]
        return bc_api_token, response

    # def _upload_run(self, args, scan_reports):
    #     print(Style.BRIGHT + colored("Sucessfully configured Bridgecrew.cloud...", 'green',
    #                                  attrs=['bold']) + Style.RESET_ALL)
    #     self.persist_repository(args.directory[0])
    #     print(Style.BRIGHT + colored("Metadata upload complete", 'green',
    #                                  attrs=['bold']) + Style.RESET_ALL)
    #     self.persist_scan_results(scan_reports)
    #     print(Style.BRIGHT + colored("Report upload complete", 'green',
    #                                  attrs=['bold']) + Style.RESET_ALL)
    #     self.commit_repository(args.branch)
    #     print(Style.BRIGHT + colored(
    #         "COMPLETE! Your Bridgecrew dashboard is available here: https://bridgecrew.cloud \n"
    #         "Login information should be in your email inbox", 'green', attrs=['bold']) + Style.RESET_ALL)

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
                            "exist with this email address. Please login bridgecrew.cloud to retrieve access key");

    def _input_orgname(self):
        valid = False
        result = None
        while not valid:
            result = str(
                input('Organization name (this will create an account with matching identifier): ')).lower().strip()  # nosec
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

    def _input_email(self):
        valid_email = False
        while not valid_email:
            email = str(input('E-Mail:')).lower().strip()  # nosec
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
                sleep(1)


bc_integration = BcPlatformIntegration()
