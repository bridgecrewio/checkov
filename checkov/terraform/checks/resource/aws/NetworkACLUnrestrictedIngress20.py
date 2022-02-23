from checkov.terraform.checks.resource.aws.AbsNACLUnrestrictedIngress import AbsNACLUnrestrictedIngress


class NACLUnrestrictedIngress20(AbsNACLUnrestrictedIngress):
    def __init__(self):
        super().__init__(check_id="CKV_AWS_230", port=20)


check = NACLUnrestrictedIngress20()
