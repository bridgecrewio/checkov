from checkov.terraform.checks.resource.aws.AbsNACLUnrestrictedIngress import AbsNACLUnrestrictedIngress


class NACLUnrestrictedIngress22(AbsNACLUnrestrictedIngress):
    def __init__(self):
        super().__init__(check_id="CKV_AWS_232", port=22)


check = NACLUnrestrictedIngress22()
