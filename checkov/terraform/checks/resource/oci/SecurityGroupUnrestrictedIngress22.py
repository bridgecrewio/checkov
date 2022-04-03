from checkov.terraform.checks.resource.oci.AbsSecurityGroupUnrestrictedIngress import \
    AbsSecurityGroupUnrestrictedIngress


class SecurityGroupUnrestrictedIngress22(AbsSecurityGroupUnrestrictedIngress):
    def __init__(self):
        super().__init__(check_id="CKV_OCI_22", port=22)


check = AbsSecurityGroupUnrestrictedIngress("CKV_OCI_22", 22)
