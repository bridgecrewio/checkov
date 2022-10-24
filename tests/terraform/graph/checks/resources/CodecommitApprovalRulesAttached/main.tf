resource "aws_codecommit_repository" "pass" {
  repository_name = "MyTestRepository"
  description     = "This is the Sample App Repository"
}

resource "aws_codecommit_approval_rule_template_association" "example" {
  approval_rule_template_name = aws_codecommit_approval_rule_template.example.name
  repository_name             = aws_codecommit_repository.pass.repository_name
}

resource "aws_codecommit_repository" "fail" {
  repository_name = "MyTestRepository"
  description     = "This is the Sample App Repository"
}