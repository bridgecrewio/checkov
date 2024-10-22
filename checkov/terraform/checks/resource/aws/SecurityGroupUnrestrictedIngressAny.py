from checkov.terraform.checks.resource.aws.AbsSecurityGroupUnrestrictedIngress import\
    AbsSecurityGroupUnrestrictedIngress


class SecurityGroupUnrestrictedIngressAll(AbsSecurityGroupUnrestrictedIngress):
    def __init__(self):
        super().__init__(check_id="CKV_AWS_277", port=-1)


check = SecurityGroupUnrestrictedIngressAll()
