provider "aws" {
  region = "us-west-1"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
#  s3_force_path_style         = true
  access_key                  = "mock_access_key"
  secret_key                  = "mock_secret_key"
}

provider "aws" {
  region = "eu-west-1"
  alias = "eu_west"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
#  s3_force_path_style         = true
  access_key                  = "mock_access_key"
  secret_key                  = "mock_secret_key"
}

module "level2" {
  source   = "./nesting_l2"
}

module "level2_2" {
  source   = "./nesting_l2_2"
  providers = {
    aws =  aws.eu_west
  }
}




resource "aws_s3_bucket_object" "this_other_file" {
  bucket   = "your_bucket_name"
  key      = "key"
  source   = "source"

}
