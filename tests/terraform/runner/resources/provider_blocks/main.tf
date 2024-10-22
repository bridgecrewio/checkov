provider "aws" {
  alias      = "provider_check_1"
  region     = "us-west-1"
}

provider "aws" {
  alias      = "provider_check_2"
  region     = "ap-northeast-2"
}

provider "aws" {
  alias      = "provider_check_3"
  region     = "ap-northeast-2"
  default_tags {
    tags = {
      Environment = "Test"
      Name        = "Provider Tag"
    }
  }
}

provider "aws" {
  alias      = "provider_check_4"
  region     = "ap-northeast-2"
  default_tags {
  }
}

provider "aws" {
  alias      = "provider_check_5"
}
