from checkov.common.util.config_utils import should_scan_hcl_files

SCAN_HCL_FLAG = "CKV_SCAN_HCL"
SUPPORTED_FILE_EXTENSIONS = [".tf", ".yml", ".yaml", ".json", ".template"]
if should_scan_hcl_files():
    SUPPORTED_FILE_EXTENSIONS.append(".hcl")
ANY_VALUE = "CKV_ANY"
DOCKER_IMAGE_REGEX = r'(?:[^\s\/]+/)?([^\s:]+):?([^\s]*)'
access_key_pattern = "(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])" # nosec
secret_key_pattern = "(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])" # nosec
linode_token_pattern ="(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{64}(?![A-Za-z0-9/+=])" # nosec
bridgecrew_token_pattern="^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z" # nosec
YAML_COMMENT_MARK = '#'