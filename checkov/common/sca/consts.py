from enum import Enum
from typing import Optional, Dict

from checkov.common.sast.consts import SastLanguages


class ScaPackageFile(Enum):
    PACKAGE_JSON = 'package.json'
    PACKAGE_JSON_LOCK = 'package-lock.json'
    POM_XML = 'pom.xml'
    BUILD_GRADLE = 'build.gradle'
    PIPFILE = 'Pipfile'
    PIPFILE_LOCK = 'Pipfile.lock'


sca_package_to_sast_lang_map: Dict[ScaPackageFile, SastLanguages] = {
    ScaPackageFile.PACKAGE_JSON: SastLanguages.JAVASCRIPT,
    ScaPackageFile.PACKAGE_JSON_LOCK: SastLanguages.JAVASCRIPT,
    ScaPackageFile.POM_XML: SastLanguages.JAVA,
    ScaPackageFile.BUILD_GRADLE: SastLanguages.JAVA,
    ScaPackageFile.PIPFILE: SastLanguages.PYTHON,
    ScaPackageFile.PIPFILE_LOCK: SastLanguages.PYTHON
}


def get_package_by_str(package_name: str) -> Optional[ScaPackageFile]:
    for enum_member in ScaPackageFile:
        if enum_member.value == package_name:
            return enum_member
    return None
