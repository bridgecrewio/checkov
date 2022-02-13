from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGoogleComputeFirewallUnrestrictedIngress import AbsGoogleComputeFirewallUnrestrictedIngress

PORT = 21


class GoogleComputeFirewallUnrestrictedIngress21(AbsGoogleComputeFirewallUnrestrictedIngress):
    def __init__(self):
        name = "Ensure Google compute firewall ingress does not allow unrestricted FTP access"
        id = "CKV_GCP_75"
        supported_resources = ['google_compute_firewall']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, port=PORT)


check = GoogleComputeFirewallUnrestrictedIngress21()
