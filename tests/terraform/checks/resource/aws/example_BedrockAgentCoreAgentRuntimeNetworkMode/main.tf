# fail - PUBLIC network mode gives the runtime internet egress
resource "aws_bedrockagentcore_agent_runtime" "public" {
  agent_runtime_name = "public_runtime"
  network_configuration {
    network_mode = "PUBLIC"
  }
}

# fail - missing network configuration
resource "aws_bedrockagentcore_agent_runtime" "missing_network" {
  agent_runtime_name = "missing_network_runtime"
}

# pass - VPC network mode
resource "aws_bedrockagentcore_agent_runtime" "vpc" {
  agent_runtime_name = "vpc_runtime"
  network_configuration {
    network_mode = "VPC"
    network_mode_config {
      security_groups = ["sg-12345678"]
      subnets         = ["subnet-12345678"]
    }
  }
}
