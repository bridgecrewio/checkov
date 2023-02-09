from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGoogleComputeFirewallUnrestrictedIngress import AbsGoogleComputeFirewallUnrestrictedIngress

PORT = 80


class GoogleComputeFirewallUnrestrictedIngress80(AbsGoogleComputeFirewallUnrestrictedIngress):
    def __init__(self):
        name = "Ensure Google compute firewall ingress does not allow unrestricted http port 80 access"
        id = "CKV_GCP_106"
        supported_resources = ['google_compute_firewall']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, port=PORT)


check = GoogleComputeFirewallUnrestrictedIngress80()
