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


def setup_bridgecrew_credentials(bc_api_key):
    credentials_api_url = f"{BC_API_URL}/api/v1/integrations/types/checkov/getCreds"
    try:
        request = http.request('GET', credentials_api_url, headers={"Authorization": bc_api_key})
        response = json.loads(request.data.decode('utf8'))
        timestamp = response['timestamp']
        credentials = response['credentials']
        return timestamp, credentials
    except Exception as e:
        logging.error(f"Failed to get customer assumed role\n{e}")


def persist_repository(root_dir, credentials, timestamp):
    pass
