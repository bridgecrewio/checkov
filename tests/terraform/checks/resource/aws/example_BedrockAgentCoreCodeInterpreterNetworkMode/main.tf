# fail - PUBLIC network mode gives the tool internet egress
resource "aws_bedrockagentcore_code_interpreter" "public" {
  name = "public_interpreter"
  network_configuration {
    network_mode = "PUBLIC"
  }
}

# fail - missing network configuration
resource "aws_bedrockagentcore_code_interpreter" "missing_network" {
  name = "missing_network_interpreter"
}

# pass - VPC network mode
resource "aws_bedrockagentcore_code_interpreter" "vpc" {
  name = "vpc_interpreter"
  network_configuration {
    network_mode = "VPC"
    vpc_config {
      security_groups = ["sg-12345678"]
      subnets         = ["subnet-12345678"]
    }
  }
}

# pass - SANDBOX is isolated with no internet access (S3 only)
resource "aws_bedrockagentcore_code_interpreter" "sandbox" {
  name = "sandbox_interpreter"
  network_configuration {
    network_mode = "SANDBOX"
  }
}
