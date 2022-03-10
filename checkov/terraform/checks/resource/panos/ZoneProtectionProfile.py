from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class ZoneProtectionProfile(BaseResourceCheck):
    def __init__(self):
        name = "Ensure a Zone Protection Profile is defined within Security Zones"
        id = "CKV_PAN_14"
        supported_resources = ['panos_zone', 'panos_zone_entry', 'panos_panorama_zone']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):

        # Report the area of evaluation
        self.evaluated_keys = ['zone_profile']
    
        # Check there is a Zone Protection Profile defined in the resource
        if 'zone_profile' in conf:

            # Get the Zone Protection Profile
            profile_definition = conf.get('zone_profile')

            # There can only be one "zone_profile" or Terraform fails at the "plan" stage
            if profile_definition[0].strip() == "":
                
                # An empty string is no Zone Protection Profile, which is a fail
                return CheckResult.FAILED
            
            else:
                
                # A non-empty string is a Zone Protection Profile being used, which is a pass
                return CheckResult.PASSED

        # If the "zone_profile" attribute is not defined, there is no Zone Protection Profile for this zone, which is a fail
        return CheckResult.FAILED

check = ZoneProtectionProfile()
