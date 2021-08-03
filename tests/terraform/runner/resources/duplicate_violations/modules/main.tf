
data "aws_iam_policy_document" "restrictions" {

  # do not allow the account to leave the org except for the exempt
  statement {
    effect  = "Deny"
    resources = [
      "*",
    ]
  }

}

resource "aws_organizations_policy" "restrictions" {
  name    = "${var.account_name}-restrictions"
  content = data.aws_iam_policy_document.restrictions.json
}
