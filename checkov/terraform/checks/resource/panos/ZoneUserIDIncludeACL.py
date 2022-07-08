from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class ZoneUserIDIncludeACL(BaseResourceCheck):
    def __init__(self):
        name = "Ensure an Include ACL is defined for a Zone when User-ID is enabled"
        id = "CKV_PAN_15"
        supported_resources = ['panos_zone', 'panos_panorama_zone']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):

        # Report the area of evaluation
        self.evaluated_keys = ['include_acls']
    
        # Get User-ID status, boolean value
        user_id_enabled = conf.get('enable_user_id')

        # Check if User-ID is enabled in the zone
        if user_id_enabled:

            # Then check if an Include ACL is defined for User-ID
            if 'include_acls' in conf:

                # Get the Include ACL attribute
                acls = conf.get('include_acls')[0]

                # Cycle through each item in the Include ACL list
                for acl in acls:

                    # Check for empty strings
                    if acl.strip() == "":
                        
                        # An empty string is no ACL, which is a fail
                        return CheckResult.FAILED
                
                # No empty strings found in Include ACL definition, so this is a pass
                return CheckResult.PASSED

            else:
                # No Include ACl for User-ID is a fail
                return CheckResult.FAILED

        # If User-ID is not enabled for the zone, the Include ACL check is not needed
        else:
            return CheckResult.PASSED

check = ZoneUserIDIncludeACL()
