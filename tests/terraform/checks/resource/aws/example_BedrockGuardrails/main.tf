resource "aws_bedrockagent_agent" "fail" {
  agent_name                  = "my-agent-name"
  agent_resource_role_arn     = aws_iam_role.example.arn
  idle_session_ttl_in_seconds = 500
  foundation_model            = "anthropic.claude-v2"
}

resource "aws_bedrockagent_agent" "pass" {
  agent_name                  = "my-agent-name"
  agent_resource_role_arn     = aws_iam_role.example.arn
  idle_session_ttl_in_seconds = 500
  foundation_model            = "anthropic.claude-v2"

  guardrail_configuration {
    guardrail_identifier = "foo"
    guardrail_version = 1
  }
}