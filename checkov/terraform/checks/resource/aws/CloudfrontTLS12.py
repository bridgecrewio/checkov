from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudFrontTLS12(BaseResourceValueCheck):
    def __init__(self):
        name = "Verify CloudFront Distribution Viewer Certificate is using TLS v1.2"
        id = "CKV_AWS_174"
        supported_resources = ["aws_cloudfront_distribution"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "viewer_certificate" in conf.keys():
            # check if cloudfront_default_certificate is true then this could use less than tls 1.2
            viewer_certificate = conf["viewer_certificate"][0]
            if 'cloudfront_default_certificate' in viewer_certificate:
                #is not using the default certificate
                if viewer_certificate["cloudfront_default_certificate"] is not True:
                    #these protocol versions
                    if "minimum_protocol_version" in viewer_certificate:
                        protocol=viewer_certificate["minimum_protocol_version"][0]
                        if protocol in ['TLSv1.2_2018', 'TLSv1.2_2019', 'TLSv1.2_2021']:
                            return CheckResult.PASSED

        #No cert specified so using default which can be less that tls 1.2
        return CheckResult.FAILED

    def get_inspected_key(self):

        return "viewer_certificate/[0]/minimum_protocol_version"

    def get_expected_values(self):
        return ['TLSv1.2_2018', 'TLSv1.2_2019', 'TLSv1.2_2021']


check = CloudFrontTLS12()