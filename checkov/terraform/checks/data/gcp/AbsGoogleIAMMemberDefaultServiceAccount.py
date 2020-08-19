import re

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.data.base_check import BaseDataCheck

# Default Compute -compute@developer.gserviceaccount.com
# Default App Spot @appspot.gserviceaccount.com
DEFAULT_SA = re.compile(".*-compute@developer\.gserviceaccount\.com|.*@appspot\.gserviceaccount\.com")


class AbsGoogleIAMMemberDefaultServiceAccount(BaseDataCheck):
    def __init__(self, name, id, categories, supported_data):
        super().__init__(name, id, categories, supported_data)

    def scan_data_conf(self, conf):
        if any(re.match(DEFAULT_SA, member) for member in conf['members'][0]):
            return CheckResult.FAILED
        return CheckResult.PASSED
