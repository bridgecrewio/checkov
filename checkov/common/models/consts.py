import re

from checkov.common.util.config_utils import should_scan_hcl_files

SCAN_HCL_FLAG = "CKV_SCAN_HCL"
SUPPORTED_FILE_EXTENSIONS = [".tf", ".yml", ".yaml", ".json", ".template"]
SUPPORTED_FILES = ["Dockerfile"]
if should_scan_hcl_files():
    SUPPORTED_FILE_EXTENSIONS.append(".hcl")
ANY_VALUE = "CKV_ANY"
DOCKER_IMAGE_REGEX = re.compile(r'(?:[^\s\/]+\/)?([^\s:]+):?([^\s]*)')
access_key_pattern = re.compile("(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])")  # nosec
secret_key_pattern = re.compile("(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])")  # nosec
linode_token_pattern = re.compile("(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{64}(?![A-Za-z0-9/+=])")  # nosec
bridgecrew_token_pattern = re.compile(r"^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z")  # nosec
panos_api_key_pattern = re.compile(r"^LUFRPT1[a-zA-Z0-9]+==\Z")  # nosec
YAML_COMMENT_MARK = '#'
