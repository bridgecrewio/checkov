import os
import tempfile
from pathlib import Path

from checkov.common.models.enums import CheckFailLevel
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.common.util.http_utils import normalize_bc_url
from checkov.common.util.type_forcers import convert_str_to_bool, force_int
from checkov.version import version


class EnvVarsConfig:
    def __init__(self) -> None:
        self.BC_API_URL = normalize_bc_url(os.getenv("BC_API_URL"))
        self.BC_ENABLE_PERSIST_GRAPHS = convert_str_to_bool(os.getenv("BC_ENABLE_PERSIST_GRAPHS", True))
        self.BC_PERSIST_GRAPHS_TIMEOUT = force_int(os.getenv("BC_PERSIST_GRAPHS_TIMEOUT", 60))
        self.BC_ROOT_DIR = os.getenv("BC_ROOT_DIR", "")
        self.BC_SKIP_MAPPING = convert_str_to_bool(os.getenv("BC_SKIP_MAPPING", False))
        self.BC_SOURCE = os.getenv("BC_SOURCE", "cli")
        self.BC_SOURCE_VERSION = os.getenv("BC_SOURCE_VERSION", version)
        self.CACHE_DIR = convert_str_to_bool(os.getenv("CKV_CACHE_DIR", str(Path(tempfile.gettempdir()) / "cache")))
        self.CHECK_FAIL_LEVEL = os.getenv("CHECKOV_CHECK_FAIL_LEVEL", CheckFailLevel.ERROR)
        self.CREATE_COMPLEX_VERTICES = convert_str_to_bool(os.getenv("CREATE_COMPLEX_VERTICES", True))
        self.CHECKOV_ENABLE_DATAS_FOREACH_HANDLING = os.getenv('CHECKOV_ENABLE_DATAS_FOREACH_HANDLING', 'False')
        self.CHECKOV_EXPERIMENTAL_TERRAFORM_MANAGED_MODULES = convert_str_to_bool(os.getenv('CHECKOV_EXPERIMENTAL_TERRAFORM_MANAGED_MODULES', False))
        self.CREATE_EDGES = convert_str_to_bool(os.getenv("CREATE_EDGES", True))
        self.CREATE_MARKDOWN_HYPERLINKS = convert_str_to_bool(os.getenv("CHECKOV_CREATE_MARKDOWN_HYPERLINKS", False))
        self.CREATE_SCA_IMAGE_REPORTS_FOR_IR = convert_str_to_bool(
            os.getenv("CHECKOV_CREATE_SCA_IMAGE_REPORTS_FOR_IR", True)
        )
        # default version is set inside the relevant code
        self.CYCLONEDX_SCHEMA_VERSION = os.getenv("CHECKOV_CYCLONEDX_SCHEMA_VERSION", "")
        self.DISPLAY_REGISTRY_URL = convert_str_to_bool(os.getenv("CHECKOV_DISPLAY_REGISTRY_URL", False))
        self.ENABLE_FOREACH_HANDLING = convert_str_to_bool(os.getenv("CHECKOV_ENABLE_FOREACH_HANDLING", True))
        self.ENABLE_MODULES_FOREACH_HANDLING = convert_str_to_bool(
            os.getenv("CHECKOV_ENABLE_MODULES_FOREACH_HANDLING", True)
        )
        self.EXPERIMENTAL_GRAPH_DEBUG = convert_str_to_bool(os.getenv("CHECKOV_EXPERIMENTAL_GRAPH_DEBUG", False))
        self.EXPIRATION_TIME_IN_SEC = force_int(os.getenv("CHECKOV_EXPIRATION_TIME_IN_SEC", 604800))
        self.GITHUB_CONF_DIR_NAME = os.getenv("CKV_GITHUB_CONF_DIR_NAME", "github_conf")
        self.GITHUB_CONFIG_FETCH_DATA = convert_str_to_bool(os.getenv("CKV_GITHUB_CONFIG_FETCH_DATA", True))
        self.GITLAB_CONF_DIR_NAME = os.getenv("CKV_GITLAB_CONF_DIR_NAME", "gitlab_conf")
        self.GITLAB_CONFIG_FETCH_DATA = convert_str_to_bool(os.getenv("CKV_GITLAB_CONFIG_FETCH_DATA", True))
        self.GRAPH_FRAMEWORK = os.getenv("CHECKOV_GRAPH_FRAMEWORK", "RUSTWORKX")
        self.IGNORED_DIRECTORIES = os.getenv("CKV_IGNORED_DIRECTORIES", "node_modules,.terraform,.serverless")
        self.IGNORE_HIDDEN_DIRECTORIES = convert_str_to_bool(os.getenv("CKV_IGNORE_HIDDEN_DIRECTORIES", True))
        self.MAX_FILE_SIZE = force_int(os.getenv("CHECKOV_MAX_FILE_SIZE", 5_000_000))  # 5 MB is default limit
        self.MAX_IAC_FILE_SIZE = force_int(os.getenv("CHECKOV_MAX_IAC_FILE_SIZE", 50_000_000))  # 50 MB is default limit
        self.NO_OUTPUT = convert_str_to_bool(os.getenv("CHECKOV_NO_OUTPUT", False))
        self.OUTPUT_CODE_LINE_LIMIT = force_int(os.getenv("CHECKOV_OUTPUT_CODE_LINE_LIMIT", 50))
        self.PARSE_ERROR_FAIL = convert_str_to_bool(os.getenv("CKV_PARSE_ERROR_FAIL", False))
        self.RENDER_ASYNC_MAX_WORKERS = force_int(os.getenv("RENDER_ASYNC_MAX_WORKERS", 50))
        self.RENDER_EDGES_DUPLICATE_ITER_COUNT = force_int(os.getenv("RENDER_EDGES_DUPLICATE_ITER_COUNT", 4))
        self.RENDER_EDGES_DUPLICATE_PERCENT = force_int(os.getenv("RENDER_EDGES_DUPLICATE_PERCENT", 90))
        self.RENDER_MAX_LEN = force_int(os.getenv("CHECKOV_RENDER_MAX_LEN", 10000))
        self.RENDER_VARIABLES_ASYNC = convert_str_to_bool(os.getenv("RENDER_VARIABLES_ASYNC", False))
        self.RUN_IN_DOCKER = convert_str_to_bool(os.getenv("RUN_IN_DOCKER", False))
        self.REQUEST_MAX_TRIES = force_int(os.getenv("REQUEST_MAX_TRIES", 3))
        self.RUN_SECRETS_MULTIPROCESS = convert_str_to_bool(os.getenv("RUN_SECRETS_MULTIPROCESS", False))
        self.SLEEP_BETWEEN_REQUEST_TRIES = force_int(os.getenv("SLEEP_BETWEEN_REQUEST_TRIES", 1))
        self.SLS_FILE_MASK = os.getenv("CKV_SLS_FILE_MASK", "serverless.yml,serverless.yaml").split(",")
        self.VALIDATE_SECRETS = convert_str_to_bool(os.getenv("CKV_VALIDATE_SECRETS", False))
        self.WORKDIR = os.getenv("WORKDIR", "")

        # possibly not used anymore 'checkov/terraform/graph_builder/utils.generate_possible_strings_from_wildcards()'
        self.MAX_WILDCARD_ARR_SIZE = force_int(os.getenv("MAX_WILDCARD_ARR_SIZE", 10))
        # is also defined as a flag, need to remove env var references in code
        self.EXTERNAL_MODULES_DIR = os.getenv("EXTERNAL_MODULES_DIR", DEFAULT_EXTERNAL_MODULES_DIR)
        # is also defined as a flag, need to remove env var references in code
        self.BC_CA_BUNDLE = os.getenv("BC_CA_BUNDLE")
        # is also defined as a flag, need to remove env var references in code
        self.PRISMA_API_URL = os.getenv("PRISMA_API_URL", "https://api0.prismacloud.io")
        # need to fix usage, because the env var value is set inside the code
        self.GITHUB_CONF_DIR_PATH = os.getenv("CKV_GITHUB_CONF_DIR_PATH")
        self.ENABLE_DEFINITION_KEY = os.getenv("ENABLE_DEFINITION_KEY", False)
        self.SKIP_PACKAGE_UPDATE_CHECK = convert_str_to_bool(os.getenv("CKV_SKIP_PACKAGE_UPDATE_CHECK", False))
        self.CKV_SUPPORT_ALL_RESOURCE_TYPE = os.getenv('CKV_SUPPORT_ALL_RESOURCE_TYPE', False)
        self.HCL_PARSE_TIMEOUT_SEC = force_int(os.getenv("HCL_PARSE_TIMEOUT_SEC", 10))
        self.ENABLE_DOTNET_CPM = os.getenv('ENABLE_DOTNET_CPM', False)
        self.JAVA_FULL_DT = os.getenv('JAVA_FULL_DT', False)
        self.PROXY_CA_PATH = os.getenv('PROXY_CA_PATH', None)
        self.PROXY_URL = os.getenv('PROXY_URL', None)
        self.PROXY_HEADER_VALUE = os.getenv('PROXY_HEADER_VALUE', None)
        self.PROXY_HEADER_KEY = os.getenv('PROXY_HEADER_KEY', None)
        self.ENABLE_CONFIG_FILE_VALIDATION = convert_str_to_bool(os.getenv("ENABLE_CONFIG_FILE_VALIDATION", False))
        self.RAW_TF_IN_GRAPH_ENV = convert_str_to_bool(os.getenv("RAW_TF_IN_GRAPH", "False"))


env_vars_config = EnvVarsConfig()
