from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class PolicyNoSrcAnyDstAny(BaseResourceCheck):
    def __init__(self):
        name = "Ensure security rules do not have 'source_addresses' and 'destination_addresses' both containing values of 'any' "
        id = "CKV_PAN_7"
        supported_resources = ['panos_security_policy','panos_security_rule_group']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
    
        # Check there is a rule defined in the resource
        if 'rule' in conf:

            # Report the area of evaluation
            self.evaluated_keys = ['rule']

            # Get all the rules defined in the resource
            rules = conf.get('rule')

            # Iterate over each rule
            for secrule in rules:

                # Check if source_addresses is defined in the resource
                if 'source_addresses' in secrule:

                    # If source_addresses is defined, get the value
                    source_addresses = secrule.get('source_addresses')
                    
                    # source_addresses can have a list of values, so iterate over each value
                    for src_address in source_addresses[0]:
                    
                        # The value "any" is overly permissive for source_addresses only if combined with destination_address=any...
                        if src_address == "any":

                            # ...so check if destination_addresses is defined in the resource
                            if 'destination_addresses' in secrule:

                                # If destination_addresses is defined, get the value
                                destination_addresses = secrule.get('destination_addresses')

                                # destination_addresses can have a list of values, so iterate over each value
                                for dst_address in destination_addresses[0]:
                                
                                    # If the value of destination_addresses is also "any" as well as source_addresses=any, this is overly permissive
                                    if dst_address == "any":
                                        return CheckResult.FAILED
                            
                            else:
                                # If "destination_addresses" attribute is not defined, this is not valid and will fail during Terraform plan stage, and should therefore be a fail
                                return CheckResult.FAILED

                else:
                    # If "source_addresses" attribute is not defined, this is not valid and will fail during Terraform plan stage, and should therefore be a fail
                    return CheckResult.FAILED
                
            # We have been through all rules and not found one with failure where source_addresses and destination_addresses both have the value 'any', so this is a pass
            return CheckResult.PASSED
            
        # If there's no rules we have nothing to check
        return CheckResult.UNKNOWN


check = PolicyNoSrcAnyDstAny()
