provider "aws" {
  region = "us-west-1"
}

provider "aws" {
  region = "eu-west-1"
  alias = "eu-west-1"
}

# The resources in the Provider block are not explicitly associated to this resource.
module "example" {
  source    = "./example"
  providers = {
    aws = aws.eu-west-1
  }
}