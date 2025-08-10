#
# WARNING: Line numbers matter in this test!
#          Update test_module_skip if a change is made!
#

module "test_module" {
  source = "./module"

  #checkov:skip=CKV_AWS_19:Skip encryption
}

resource "aws_s3_bucket" "outside" {
  bucket = "outside-bucket"

  #checkov:skip=CKV_AWS_19:Skip encryption
}
