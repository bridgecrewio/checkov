from checkov.terraform.checks.resource.aws.AbsNACLUnrestrictedIngress import AbsNACLUnrestrictedIngress


class NACLUnrestrictedIngress3389(AbsNACLUnrestrictedIngress):
    def __init__(self):
        super().__init__(check_id="CKV_AWS_231", port=3389)


check = NACLUnrestrictedIngress3389()
