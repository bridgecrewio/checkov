import os

DEFAULT_EXTERNAL_MODULES_DIR = ".external_modules"
RESOLVED_MODULE_ENTRY_NAME = "__resolved__"
START_LINE = '__startline__'
END_LINE = '__endline__'

DEV_API_GET_HEADERS = {
    'Accept': 'application/json'
}

DEV_API_POST_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

PRISMA_API_GET_HEADERS = {
    'Accept': 'application/json; charset=UTF-8'
}

PARSE_ERROR_FAIL_FLAG = 'CKV_PARSE_ERROR_FAIL'

PRISMA_PLATFORM = 'Prisma Cloud Code Security'
BRIDGECREW_PLATFORM = 'Bridgecrew'

MAX_IAC_FILE_SIZE = int(os.getenv('CHECKOV_MAX_IAC_FILE_SIZE', '50_000_000'))  # 50 MB is default limit

CHECKOV_RUN_SCA_PACKAGE_SCAN_V2 = os.getenv('CHECKOV_RUN_SCA_PACKAGE_SCAN_V2', 'true').lower() == 'true'

RESOURCE_ATTRIBUTES_TO_OMIT_UNIVERSAL_MASK = '*'
