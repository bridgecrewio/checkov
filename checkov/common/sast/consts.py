from enum import Enum
from typing import List, Any, Set
from pathlib import Path


SAST_FRAMEWORK_PREFIX = 'sast'
CDK_FRAMEWORK_PREFIX = 'cdk'
# checkov/checkov/cdk/checks
CDK_CHECKS_DIR_PATH = Path(__file__).parent.parent.parent / CDK_FRAMEWORK_PREFIX / "checks"


class SastLanguages(Enum):
    @classmethod
    def list(cls) -> List[Any]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def set(cls) -> Set["SastLanguages"]:
        return set(cls)

    PYTHON = 'python'
    JAVA = 'java'
    JAVASCRIPT = 'javascript'
    TYPESCRIPT = 'typescript'
    GOLANG = 'golang'


class CDKLanguages(Enum):
    @classmethod
    def list(cls) -> List[Any]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def set(cls) -> Set["CDKLanguages"]:
        return set(cls)

    PYTHON = 'python'
    TYPESCRIPT = 'typescript'


class BqlVersion(str, Enum):
    def __str__(self) -> str:
        return self.value

    V0_1 = '0.1'
    V0_2 = '0.2'


def get_bql_version_from_string(version_str: str) -> str:
    for version in BqlVersion:
        if version.value == version_str:
            return version
    return ''


SUPPORT_FILE_EXT = {
    SastLanguages.PYTHON: ['py'],
    SastLanguages.JAVA: ['java'],
    SastLanguages.JAVASCRIPT: ['js'],
    SastLanguages.TYPESCRIPT: ['ts'],
    SastLanguages.GOLANG: ['go'],
}

FILE_EXT_TO_SAST_LANG = {
    'py': SastLanguages.PYTHON,
    'java': SastLanguages.JAVA,
    'js': SastLanguages.JAVASCRIPT,
    'ts': SastLanguages.TYPESCRIPT,
    'go': SastLanguages.GOLANG,
}

POLICIES_ERRORS = 'policies_errors'
POLICIES_ERRORS_COUNT = 'policies_errors_count'
ENGINE_NAME = "engine_name"
SOURCE_FILES_COUNT = "source_files_count"
POLICY_COUNT = "policy_count"
