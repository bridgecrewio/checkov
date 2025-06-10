import boto3
import os
import tempfile
from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.loader import ModuleLoader


class S3Loader(ModuleLoader):
    def __init__(self):
        super().__init__()
        self.s3_client = boto3.client('s3')

    def _find_module_path(self, module_params):
        # to determine the exact path here would be almost a duplicate of the git_loader functionality
        return ""

    def discover(self, module_params):
        # Check for valid AWS credentials and access to the S3 object
        try:
            bucket_name, key = self._parse_s3_uri(module_params.module_source)
            self.s3_client.head_object(Bucket=bucket_name, Key=key)
            self.logger.info("AWS credentials are valid and access to the S3 object is verified.")
        except self.s3_client.exceptions.ClientError:
            self.logger.error("Failed to access S3 object. Verify that you have permission to access the object and that the path is correct.")
            raise

    def _is_matching_loader(self, module_params):
        return module_params.module_source.startswith("s3::")

    def _parse_s3_uri(self, uri):
        if not uri.startswith("s3::"):
            raise ValueError("Invalid S3 URI")
        uri = uri[4:]

        # get bucket and object
        if uri.startswith('https'):
            # get after .com, remove leading slash, split on / again
            no_prefix = uri.split(".com", 1)[1][1:].split("/", 1)
        else:
            # just remove leading slash, split on /
            no_prefix = uri[1:].split("/", 1)
        # strip leading ./ if present
        if no_prefix[1].startswith("./"):
            no_prefix[1] = no_prefix[1][2:]
        return no_prefix[0], no_prefix[1]

    def _download_from_s3(self, bucket_name, key):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            self.s3_client.download_file(bucket_name, key, tmp_file.name)
            tmp_file.close()
            return tmp_file.name

    def cleanup(self, downloaded_path):
        if os.path.exists(downloaded_path):
            os.remove(downloaded_path)

    def _load_module(self, module_params):
        # feels weird i have to do this, isn't that the whole point of the function i'm using?
        if not self._is_matching_loader(module_params):
            return ModuleContent(dir=None, failed_url=module_params.module_source)
        try:
            bucket_name, key = self._parse_s3_uri(module_params.module_source)
            downloaded_path = self._download_from_s3(bucket_name, key)
        except Exception as e:
            self.logger.warning(f"Failed to download S3 module {module_params.module_source} because of {e}")
            return ModuleContent(dir=None, failed_url=module_params.module_source)

        return_dir = downloaded_path
        self.logger.info(f'Finished loading {module_params.module_source}')
        if module_params.inner_module:
            return_dir = os.path.join(downloaded_path, module_params.inner_module)
        return ModuleContent(dir=return_dir)


loader = S3Loader()
