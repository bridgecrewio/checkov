import json
import logging
import os
from json import JSONDecodeError
from time import sleep

import boto3
import dpath
import requests
import urllib3
from botocore.exceptions import ClientError
from tqdm import trange

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_errors import BridgecrewAuthError
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.wrapper import reduce_scan_reports, enrich_and_persist_checks_metadata, persist_checks_results
from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS


# disabled when BC_SOURCE is in this list
DISALLOWED_SOURCES = ['vscode']
DEFAULT_REGION = "us-west-2"
UNAUTHORIZED_MESSAGE = 'User is not authorized to access this resource with an explicit deny'
ACCOUNT_CREATION_TIME = 180  # in seconds

try:
    http = urllib3.ProxyManager(os.environ['https_proxy'])
except KeyError:
    http = urllib3.PoolManager()


class UploadToS3Integration(BaseIntegrationFeature):

    def __init__(self, bc_integration):
        super().__init__(bc_integration, order=0)
        self.s3_client = None
        self.bucket = None
        self.repo_path = None
        self.timestamp = None
        self.credentials = None

    def is_valid(self):
        return self.bc_integration.is_integration_configured() and self.bc_integration.bc_source not in DISALLOWED_SOURCES

    def pre_scan(self):
        try:
            repo_full_path, response = self._get_s3_role(self.bc_integration.bc_api_key, self.bc_integration.repo_id)
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
        except requests.HTTPError as e:
            logging.error(f"Failed to get customer assumed role\n{e}")
            raise e
        except ClientError as e:
            logging.error(f"Failed to initiate client with credentials {self.credentials}\n{e}")
            raise e
        except JSONDecodeError as e:
            logging.error(f"Response of {self.integrations_api_url} is not a valid JSON\n{e}")
            raise e

    def post_scan(self, scan_reports):
        self._persist_repository(self.bc_integration.root_folder)
        self._persist_scan_results(scan_reports)
        self._commit_repository(self.bc_integration.branch)

    def _get_s3_role(self, bc_api_key, repo_id):
        request = http.request("POST", self.integrations_api_url, body=json.dumps({"repoId": repo_id}),
                               headers={"Authorization": bc_api_key, "Content-Type": "application/json"})
        response = json.loads(request.data.decode("utf8"))
        while 'Message' in response or 'message' in response:
            if 'Message' in response and response['Message'] == UNAUTHORIZED_MESSAGE:
                raise BridgecrewAuthError()
            if 'message' in response and "cannot be found" in response['message']:
                self.loading_output("creating role")
                request = http.request("POST", self.integrations_api_url, body=json.dumps({"repoId": repo_id}),
                                       headers={"Authorization": bc_api_key, "Content-Type": "application/json"})
                response = json.loads(request.data.decode("utf8"))

        repo_full_path = response["path"]
        return repo_full_path, response

    def _persist_repository(self, root_dir):
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

    def _persist_scan_results(self, scan_reports):
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

    def _commit_repository(self, branch):
        """
        :param branch: branch to be persisted
        Finalize the repository's scanning in bridgecrew's platform.
        """
        request = None
        try:
            request = http.request("PUT", f"{self.integrations_api_url}?source={self.bc_integration.bc_source}",
                                   body=json.dumps({"path": self.repo_path, "branch": branch}),
                                   headers={"Authorization": self.bc_integration.bc_api_key, "Content-Type": "application/json"})
            response = json.loads(request.data.decode("utf8"))
        except requests.HTTPError as e:
            logging.error(f"Failed to commit repository {self.repo_path}\n{e}")
            raise e
        except JSONDecodeError as e:
            logging.error(f"Response of {self.integrations_api_url} is not a valid JSON\n{e}")
            raise e
        finally:
            if request.status == 201 and response["result"] == "Success":
                logging.info(f"Finalize repository {self.bc_integration.repo_id} in bridgecrew's platform")
            else:
                raise Exception(f"Failed to finalize repository {self.bc_integration.repo_id} in bridgecrew's platform\n{response}")

    @staticmethod
    def loading_output(msg):
        with trange(ACCOUNT_CREATION_TIME) as t:
            for _ in t:
                t.set_description(msg)
                t.set_postfix(refresh=False)
                sleep(1)


integration = UploadToS3Integration(bc_integration)
