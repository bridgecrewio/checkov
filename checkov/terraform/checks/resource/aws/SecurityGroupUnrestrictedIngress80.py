from checkov.terraform.checks.resource.aws.AbsSecurityGroupUnrestrictedIngress import AbsSecurityGroupUnrestrictedIngress


class SecurityGroupUnrestrictedIngress80(AbsSecurityGroupUnrestrictedIngress):
    def __init__(self):
        super().__init__(check_id="CKV_AWS_260", port=80)


check = SecurityGroupUnrestrictedIngress80()
