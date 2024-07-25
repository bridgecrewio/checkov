# fail
resource "aws_bedrockagent_agent" "bedrock_agent" {
  agent_name = "example_agent_name"
}

# pass
resource "aws_bedrockagent_agent" "bedrock_agent_with_kms_key" {
  agent_name = "example_agent_name"
  customer_encryption_key_arn = aws_kms_key.example.arn
}