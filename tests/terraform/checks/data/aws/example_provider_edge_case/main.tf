provider "aws" {
  region = "us-west-1"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
#  s3_force_path_style         = true
  access_key                  = "mock_access_key"
  secret_key                  = "mock_secret_key"
}

module "level1" {
  source   = "./nesting"
  }


module "level1_2" {
  source   = "./nesting_2"
  }


resource "aws_s3_bucket_object" "this_file_2" {
  bucket   = "your_bucket_name"
  key = "some_key"
}