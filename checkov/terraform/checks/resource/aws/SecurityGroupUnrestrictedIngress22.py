from checkov.terraform.checks.resource.aws.AbsSecurityGroupUnrestrictedIngress import AbsSecurityGroupUnrestrictedIngress


class SecurityGroupUnrestrictedIngress22(AbsSecurityGroupUnrestrictedIngress):
    def __init__(self):
        super().__init__(check_id="CKV_AWS_24", port=22)


check = SecurityGroupUnrestrictedIngress22()
