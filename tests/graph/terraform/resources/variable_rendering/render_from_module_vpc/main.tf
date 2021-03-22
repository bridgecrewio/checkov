module "vpc" {
  source  = "./vpc"
  version = "2.47.0"

  name                 = "test-vpc"
  cidr                 = "172.16.0.0/16"
  private_subnets      = ["172.16.1.0/24", "172.16.2.0/24", "172.16.3.0/24"]
  public_subnets       = ["172.16.4.0/24", "172.16.5.0/24", "172.16.6.0/24"]
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                      = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"             = "1"
  }
}

locals {
  cluster_name = "test-eks-${random_string.suffix.result}"
}

data "aws_availability_zones" "available" {
}

resource "random_string" "suffix" {
  length  = 8
  special = false
}