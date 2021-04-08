variable "aws" {
  type = object({ access_key = string, secret_key = string, region = string })
}

variable "vcs_repo" {
  type = object({ identifier = string, branch = string, oauth_token = string })
}

provider "aws" {
  access_key = var.aws.access_key
  secret_key = var.aws.secret_key
  region     = var.aws.region
}
