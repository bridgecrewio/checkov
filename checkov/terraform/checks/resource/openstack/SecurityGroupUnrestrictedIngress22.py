from checkov.terraform.checks.resource.openstack.AbsSecurityGroupUnrestrictedIngress import AbsSecurityGroupUnrestrictedIngress


class SecurityGroupUnrestrictedIngress22(AbsSecurityGroupUnrestrictedIngress):
    def __init__(self):
        super().__init__(check_id="CKV_OPENSTACK_2", port=22)


check = SecurityGroupUnrestrictedIngress22()
