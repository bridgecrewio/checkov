import re

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

# Default Compute -compute@developer.gserviceaccount.com
# Default App Spot @appspot.gserviceaccount.com
DEFAULT_SA = re.compile(r".*-compute@developer\.gserviceaccount\.com|.*@appspot\.gserviceaccount\.com")


class AbsGoogleIAMMemberDefaultServiceAccount(BaseResourceCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name, id, categories, supported_resources)

    def scan_resource_conf(self, conf):
        members_conf = conf['members'][0] if 'members' in conf else conf.get('member', [])
        if any(re.match(DEFAULT_SA, str(member)) for member in members_conf):
            return CheckResult.FAILED
        return CheckResult.PASSED
