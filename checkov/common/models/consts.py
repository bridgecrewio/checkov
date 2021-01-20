SUPPORTED_FILE_EXTENSIONS = [".tf", ".yml", ".yaml", ".json", ".template"]
ANY_VALUE = "CKV_ANY"
DOCKER_IMAGE_REGEX = r'(?:[^\s\/]+/)?([^\s:]+):?([^\s]*)'
access_key_pattern = "(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])" # nosec
secret_key_pattern = "(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])" # nosec
linode_token_pattern ="(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{64}(?![A-Za-z0-9/+=])" # nosec
