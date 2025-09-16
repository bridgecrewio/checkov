resource "aws_bedrockagent_flow" "pass" {
  name               = "example"
  execution_role_arn = "arn:aws:iam::123456789012:role/service-role/AmazonBedrockExecutionRoleForFlows"
  customer_encryption_key_arn = "arn:aws:kms:us-east-1:123456789012:key/aea0cafc-355a-40a3-84f8-d52855ed333e"
}

resource "aws_bedrockagent_flow" "fail" {
  name               = "example"
  execution_role_arn = "arn:aws:iam::123456789012:role/service-role/AmazonBedrockExecutionRoleForFlows"
}
