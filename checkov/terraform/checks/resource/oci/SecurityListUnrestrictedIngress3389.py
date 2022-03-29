from checkov.terraform.checks.resource.oci.AbsSecurityListUnrestrictedIngress import AbsSecurityListUnrestrictedIngress


class SecurityListUnrestrictedIngress3389(AbsSecurityListUnrestrictedIngress):
    def __init__(self):
        super().__init__(check_id="CKV_OCI_20", port=3389, is_exposed_by_default=False)


check = SecurityListUnrestrictedIngress3389()
