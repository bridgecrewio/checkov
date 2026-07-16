# pass — attribute omitted (AWS default is 3600)
resource "aws_iam_role" "pass" {
  name               = "pass_role"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

# pass — explicit 1 hour
resource "aws_iam_role" "pass_explicit" {
  name                 = "pass_role_explicit"
  assume_role_policy   = data.aws_iam_policy_document.assume.json
  max_session_duration = 3600
}

# fail — elevated session duration (12 hours)
resource "aws_iam_role" "fail" {
  name                 = "fail_role"
  assume_role_policy   = data.aws_iam_policy_document.assume.json
  max_session_duration = 43200
}

# fail — any value above 3600
resource "aws_iam_role" "fail_boundary" {
  name                 = "fail_role_boundary"
  assume_role_policy   = data.aws_iam_policy_document.assume.json
  max_session_duration = 3601
}

# unknown — variable reference cannot be evaluated at scan time
resource "aws_iam_role" "unknown" {
  name                 = "unknown_role"
  assume_role_policy   = data.aws_iam_policy_document.assume.json
  max_session_duration = var.max_session_duration
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}
