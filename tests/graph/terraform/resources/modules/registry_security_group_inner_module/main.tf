module "web_server_sg" {
  source = "terraform-aws-modules/security-group/aws//modules/http-80"

  name        = "web-server"
  description = "Security group for web-server with HTTP ports open within VPC"
  vpc_id      = "vpc-12345678"

  ingress_cidr_blocks = ["10.10.0.0/16"]
}

resource "aws_flow_log" "related_flow_log" {
  traffic_type = ""
  vpc_id = module.web_server_sg.security_group_vpc_id
}