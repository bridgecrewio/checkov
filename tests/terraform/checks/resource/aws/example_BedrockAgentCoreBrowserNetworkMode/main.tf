# fail - PUBLIC network mode gives the tool internet egress
resource "aws_bedrockagentcore_browser" "public" {
  name = "public_browser"
  network_configuration {
    network_mode = "PUBLIC"
  }
}

# fail - missing network configuration
resource "aws_bedrockagentcore_browser" "missing_network" {
  name = "missing_network_browser"
}

# pass - VPC network mode
resource "aws_bedrockagentcore_browser" "vpc" {
  name = "vpc_browser"
  network_configuration {
    network_mode = "VPC"
    vpc_config {
      security_groups = ["sg-12345678"]
      subnets         = ["subnet-12345678"]
    }
  }
}
