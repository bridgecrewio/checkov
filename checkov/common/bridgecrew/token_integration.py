import urllib3
import boto3
import json
import logging

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
        self.credentials = None
        self.timestamp = None

    def setup_bridgecrew_credentials(self, bc_api_key):
        credentials_api_url = f"{BC_API_URL}/api/v1/integrations/types/checkov/getCreds"
        try:
            request = http.request('GET', credentials_api_url, headers={"Authorization": bc_api_key})
            response = json.loads(request.data.decode('utf8'))
            self.timestamp = response['timestamp']
            self.credentials = response['credentials']
            self.s3_client = boto3.client('s3',
                                          aws_access_key_id=self.credentials["awsAccessKeyId"],
                                          aws_secret_access_key=self.credentials["awsSecretAcessKey"],
                                          region_name=DEFAULT_REGION
                                          )
        except Exception as e:
            logging.error(f"Failed to get customer assumed role\n{e}")
            raise e

    def is_integration_configured(self):
        return all([self.timestamp, self.credentials, self.s3_client])

    def persist_repository(self, root_dir):
        # TODO
        pass
