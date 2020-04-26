import urllib3
import boto3
import json
import logging
import os

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
                                          region_name=DEFAULT_REGION
                                          )
        except Exception as e:
            logging.error(f"Failed to get customer assumed role\n{e}")
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
        for root, d_names, f_names in os.walk(root_dir):
            for file in f_names:
                _, file_extension = os.path.splitext(file)
                if file_extension in SUPPORTED_FILE_EXTENSIONS:
                    self._persist_file(os.path.join(root, file))

    def _persist_file(self, file_path):
        _, file_name = os.path.split(file_path)
        file_object_key = os.path.join(self.repo_path, file_name)
        try:
            self.s3_client.upload_file(file_path, self.bucket, file_object_key)
        except Exception as e:
            logging.error(f"failed to persist file {file_path} into S3\n{e}")
            raise e
