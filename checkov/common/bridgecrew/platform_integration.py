import urllib3
import boto3
import json
import logging
import os
from time import sleep
from .wrapper import reduce_scan_reports, persist_checks_results, enrich_and_persist_checks_metadata
from urllib3.exceptions import HTTPError
from botocore.exceptions import ClientError
from json import JSONDecodeError
import dpath.util

logging.basicConfig(level=logging.INFO)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# tell the handler to use this format
console.setFormatter(formatter)

BC_API_URL = "https://www.bridgecrew.cloud/api/v1"
SUPPORTED_FILE_EXTENSIONS = [".tf", ".yml", ".yaml", ".json", ".template"]
http = urllib3.PoolManager()
DEFAULT_REGION = "us-west-2"


class BcPlatformIntegration(object):
    def __init__(self):
        self.s3_client = None
        self.bucket = None
        self.credentials = None
        self.repo_path = None
        self.timestamp = None
        self.scan_reports = []

    def setup_bridgecrew_credentials(self, bc_api_key, repo_id):
        """
        Setup credentials against Bridgecrew's platform.
        :param repo_id: Identity string of the scanned repository, of the form <repo_owner>/<repo_name>
        :param bc_api_key: Bridgecrew issued API key
        """
        credentials_api_url = f"{BC_API_URL}/v1/integrations/types/checkov"
        try:
            request = http.request("POST", credentials_api_url, body=json.dumps({"repoId": repo_id}),
                                   headers={"Authorization": bc_api_key, "Content-Type": "application/json"})
            response = json.loads(request.data.decode("utf8"))
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
            logging.error(f"Response of {credentials_api_url} is not a valid JSON\n{e}")
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
        Persist checkov's scan result into bridgecrew's platform
        :param scan_reports: List of checkov scan reports
        """
        self.scan_reports = scan_reports
        reduced_scan_reports = reduce_scan_reports(scan_reports)
        checks_metadata_paths = enrich_and_persist_checks_metadata(scan_reports, self.s3_client, self.bucket,
                                                                   self.repo_path)
        dpath.util.merge(reduced_scan_reports, checks_metadata_paths)
        persist_checks_results(reduced_scan_reports, self.s3_client, self.bucket, self.repo_path)

    def _persist_file(self, full_file_path, relative_file_path):
        file_object_key = os.path.join(self.repo_path, relative_file_path)
        try:
            self.s3_client.upload_file(full_file_path, self.bucket, file_object_key)
        except Exception as e:
            logging.error(f"failed to persist file {full_file_path} into S3 bucket {self.bucket}\n{e}")
            raise e
