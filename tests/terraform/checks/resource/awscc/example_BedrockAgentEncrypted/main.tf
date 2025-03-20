resource "awscc_bedrock_agent" "pass" {
  agent_name = "pass"
  instruction      = "You are a helpful assistant that provides information about our company's products."
  foundation_model = "anthropic.claude-v2"
  customer_encryption_key_arn = awscc_kms_key.example.arn
}

resource "awscc_bedrock_agent" "fail" {
  agent_name = "fail"
  instruction      = "You are a helpful assistant that provides information about our company's products."
  foundation_model = "anthropic.claude-v2"
  

}