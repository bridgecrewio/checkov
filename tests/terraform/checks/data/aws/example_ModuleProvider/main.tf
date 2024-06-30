provider "aws" {
  region = "us-west-1"
}
provider "aws" {
  alias  = "usw2"
  region = "us-west-2"
}

# The resources in the Provider block are not explicitly associated to this resource.
module "example" {
  source    = "./example"
  providers = {
    aws = aws.usw2
  }
}