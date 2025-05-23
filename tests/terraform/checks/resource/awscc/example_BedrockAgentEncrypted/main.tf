resource "awscc_bedrock_agent" "pass" {
  agent_name                  = "pass"
  instruction                 = "You are a helpful assistant that provides information about our company's products."
  foundation_model            = "anthropic.claude-v2"
  customer_encryption_key_arn = "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"
}

resource "awscc_bedrock_agent" "fail" {
  agent_name       = "fail"
  instruction      = "You are a helpful assistant that provides information about our company's products."
  foundation_model = "anthropic.claude-v2"
}
