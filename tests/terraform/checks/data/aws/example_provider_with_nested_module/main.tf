provider "aws" {
  region = "us-west-1"
}

# The resources in the Provider block are not explicitly associated to this resource.
module "example" {
  source    = "./example"
}