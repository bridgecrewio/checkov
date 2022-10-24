resource "aws_codecommit_approval_rule_template" "fail" {
  name        = "MyExampleApprovalRuleTemplate"
  description = "This is an example approval rule template"

  content = <<EOF
{
    "Version": "2018-11-08",
    "DestinationReferences": ["refs/heads/master"],
    "Statements": [{
        "Type": "Approvers",
        "NumberOfApprovalsNeeded": 1,
        "ApprovalPoolMembers": ["arn:aws:sts::123456789012:assumed-role/CodeCommitReview/*"]
    }]
}
EOF
}

resource "aws_codecommit_approval_rule_template" "pass" {
  name        = "MyExampleApprovalRuleTemplate"
  description = "This is an example approval rule template"

  content = <<EOF
{
    "Version": "2018-11-08",
    "DestinationReferences": ["refs/heads/master"],
    "Statements": [{
        "Type": "Approvers",
        "NumberOfApprovalsNeeded": 2,
        "ApprovalPoolMembers": ["arn:aws:sts::123456789012:assumed-role/CodeCommitReview/*"]
    }]
}
EOF
}