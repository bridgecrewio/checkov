import urllib3
import boto3
import json
import logging
import os
from time import sleep
from urllib3.exceptions import HTTPError
from botocore.exceptions import ClientError
from json import JSONDecodeError
import dpath.util

from checkov.common.bridgecrew.platform_errors import BridgecrewAuthError
from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS
from .wrapper import reduce_scan_reports, persist_checks_results, enrich_and_persist_checks_metadata
import os

UNAUTHORIZED_MESSAGE = 'User is not authorized to access this resource with an explicit deny'


DEFAULT_REGION = "us-west-2"
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
        file_object_key = os.path.join(self.repo_path, relative_file_path)
        try:
            self.s3_client.upload_file(full_file_path, self.bucket, file_object_key)
        except Exception as e:
            logging.error(f"failed to persist file {full_file_path} into S3 bucket {self.bucket}\n{e}")
            raise e

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
