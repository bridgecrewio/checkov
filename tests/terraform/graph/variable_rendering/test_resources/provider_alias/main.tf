locals {
  tags = {
    test = "Test"
  }
}

provider "aws" {
  default_tags {
    tags = local.tags
  }
}


provider "aws" {
  alias = "test"
  default_tags {
    tags = local.tags
  }
}
