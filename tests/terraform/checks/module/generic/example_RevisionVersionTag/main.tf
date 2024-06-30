# pass

module "hash" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=26c38a66f12e7c6c93b6a2ba127ad68981a48671"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true

  tags = {
    Terraform = "true"
    Environment = "dev"
  }
}

module "sub_dir_hash" {
  source  = "git::https://github.com/terraform-aws-modules/terraform-aws-cloudwatch.git//modules/log-group?ref=60cf981e0f1ae033699e5b274440867e48289967"

  name              = "git"
  retention_in_days = 120
}

module "tag" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v5.0.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true

  tags = {
    Terraform = "true"
    Environment = "dev"
  }
}

module "shallow_clone" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?depth=1&ref=v1.2.0"
}

module "module_with_version" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-github-oidc-role"
  version = "5.39.1"
}

# fail

module "tf_registry_no_version" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-group"
}

module "looks_like_a_branch" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=some_branch_name"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true

  tags = {
    Terraform = "true"
    Environment = "dev"
  }
}

module "github_module" {
  source = "github.com/hashicorp/example"
}

module "bitbucket_module" {
  source = "bitbucket.org/hashicorp/terraform-consul-aws"
}

module "github_ssh_module" {
  source = "git@github.com:hashicorp/example.git"
}

module "generic_git_module" {
  source = "git::https://example.com/vpc.git"
}

# unknown

module "relative" {
  source = "./example"
}

module "backtrack" {
  source = "../example"
}