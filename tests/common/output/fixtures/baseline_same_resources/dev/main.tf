data "aws_iam_policy_document" "route53_policy" {
  statement {
    effect = "Allow"
    actions = [
      "route53:ListHostedZones",
      "route53:GetHostedZone",
      "route53:ListTagsForResource"
    ]
    resources = ["*"]
  }
}
