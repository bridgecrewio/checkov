provider "aws" {
  region                  = var.vpc["region"]
  shared_credentials_file = "/tmp/sts_aws_credentials/acme"
  version                 = "= 3.5.0"
}

provider "aws" {
  alias                   = "special"
  region                  = var.vpc["region"]
  shared_credentials_file = "/tmp/sts_aws_credentials/acme"
  version                 = "= 3.5.0"
}

