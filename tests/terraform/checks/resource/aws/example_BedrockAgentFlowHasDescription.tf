resource "aws_bedrockagent_flow" "pass" {
  name               = "example"
  execution_role_arn = "arn:aws:iam::123456789012:role/service-role/AmazonBedrockExecutionRoleForFlows"
  description        = "This is an example flow."
}

resource "aws_bedrockagent_flow" "fail" {
  name               = "example"
  execution_role_arn = "arn:aws:iam::123456789012:role/service-role/AmazonBedrockExecutionRoleForFlows"
}
