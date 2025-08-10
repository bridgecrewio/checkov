from checkov.terraform.checks.resource.aws.AbsSecurityGroupUnrestrictedEgress import\
    AbsSecurityGroupUnrestrictedEgress


class SecurityGroupUnrestrictedEgressAll(AbsSecurityGroupUnrestrictedEgress):
    def __init__(self):
        super().__init__(check_id="CKV_AWS_382", port=-1)


check = SecurityGroupUnrestrictedEgressAll()
