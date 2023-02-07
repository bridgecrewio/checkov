import re

SUPPORTED_FILE_EXTENSIONS = [".tf", ".yml", ".yaml", ".json", ".template", ".bicep", ".hcl"]
SUPPORTED_PACKAGE_FILES = {
    "bower.json",
    "build.gradle",
    "build.gradle.kts",
    "go.sum",
    "gradle.properties",
    "METADATA",
    "npm-shrinkwrap.json",
    "package.json",
    "package-lock.json",
    "pom.xml",
    "requirements.txt"
}
SUPPORTED_FILES = SUPPORTED_PACKAGE_FILES.union({"Dockerfile"})

DEPENDENCY_TREE_SUPPORTED_FILES = {"yarn.lock", "Gemfile", "Gemfile.lock", "go.mod", "paket.dependencies", "paket.lock", "packages.config"}

SCANNABLE_PACKAGE_FILES_EXTENSIONS = {".csproj"}

SCANNABLE_PACKAGE_FILES = SUPPORTED_PACKAGE_FILES | DEPENDENCY_TREE_SUPPORTED_FILES

ANY_VALUE = "CKV_ANY"
DOCKER_IMAGE_REGEX = re.compile(r'(?:[^\s\/]+\/)?([^\s:]+):?([^\s]*)')
access_key_pattern = re.compile("(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])")  # nosec
secret_key_pattern = re.compile("(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])")  # nosec
linode_token_pattern = re.compile("(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{64}(?![A-Za-z0-9/+=])")  # nosec
bridgecrew_token_pattern = re.compile(r"^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z")  # nosec
panos_api_key_pattern = re.compile(r"^LUFRPT1[a-zA-Z0-9]+==\Z")  # nosec
SLS_DEFAULT_VAR_PATTERN = re.compile(r"\${([^{}]+?)}")
YAML_COMMENT_MARK = '#'
TFC_HOST_NAME = "app.terraform.io"
ckv_check_id_pattern = re.compile(r"^CKV2?_[A-Za-z]*_[0-9]*$")
