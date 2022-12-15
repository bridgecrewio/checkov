variable "vpc_id" {
}

variable "ingress" {
  default = [
    {
      cidr_blocks = [
        "10.248.186.0/23",
        "10.248.180.0/23",
      ]
      from_port   = "22"
      to_port     = "22"
      protocol    = "tcp"
      description = "Allow connectivity from Atlanta VPN"
    },
    {
      cidr_blocks = [
        "10.248.80.0/23",
        "10.248.86.0/23",
      ]
      from_port   = "22"
      to_port     = "22"
      protocol    = "tcp"
      description = "Allow connectivity from Miami VPN"
    },
  ]
}

variable "egress" {
  default = [
    {
      cidr_blocks = [
        "0.0.0.0/0",
      ]
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      self        = false
      description = ""
    },
  ]
}