resource "awscc_bedrock_agent" "pass" {
  agent_name = "pass"
  instruction      = "You are a helpful assistant that provides information about our company's products."
  foundation_model = "anthropic.claude-v2"
  
  guardrail_configuration= {
    guardrail_identifier = awscc_bedrock_guardrail.example.id
  }
}

resource "awscc_bedrock_agent" "fail" {
  agent_name = "fail"
  instruction      = "You are a helpful assistant that provides information about our company's products."
  foundation_model = "anthropic.claude-v2"
  
}

resource "awscc_bedrock_guardrail" "example" {
  name                      = "example_guardrail"
  blocked_input_messaging   = "Blocked input"
  blocked_outputs_messaging = "Blocked output"
  description               = "Example guardrail"

  content_policy_config = {
    filters_config = [
      {
        input_strength  = "MEDIUM"
        output_strength = "MEDIUM"
        type            = "HATE"
      }
    ]
  }



}