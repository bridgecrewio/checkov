from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class NetworkIPsecAuthAlgorithms(BaseResourceCheck):
    def __init__(self):
        name = "Ensure IPsec profiles do not specify use of insecure authentication algorithms"
        id = "CKV_PAN_12"
        supported_resources = ['panos_ipsec_crypto_profile','panos_panorama_ipsec_crypto_profile']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
    
        # Check there are authentications defined in the resource
        if 'authentications' in conf:

            # Report the area of evaluation
            self.evaluated_keys = ['authentications']

            # Get all the algorithms
            algorithms = conf.get('authentications')

            # Iterate over each algorithm, as multiple can be defined in "authentications"
            for algo in algorithms:

                # Check for insecure algorithms, including null as a string (not a null value)
                if algo[0] in ('none', 'md5', 'sha1'):

                    # Fail if any insecure algorithms are defined for use
                    return CheckResult.FAILED

            # If no fails have been found, this is a pass
            return CheckResult.PASSED

        # If the mandatory "authentications" attribute is not defined, this is not valid, and will fail during Terraform plan stage, and should therefore be a fail
        return CheckResult.FAILED

check = NetworkIPsecAuthAlgorithms()
