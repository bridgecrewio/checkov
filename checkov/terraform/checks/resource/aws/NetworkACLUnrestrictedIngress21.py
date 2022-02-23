from checkov.terraform.checks.resource.aws.AbsNACLUnrestrictedIngress import AbsNACLUnrestrictedIngress


class NACLUnrestrictedIngress21(AbsNACLUnrestrictedIngress):
    def __init__(self):
        super().__init__(check_id="CKV_AWS_229", port=21)


check = NACLUnrestrictedIngress21()
