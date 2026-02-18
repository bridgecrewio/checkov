resource "awscc_s3_bucket" "pass" {
  bucket_name = "my-versioned-bucket"
  versioning_configuration = [{
    status = "Enabled"
  }]
}

resource "awscc_s3_bucket" "fail" {
  bucket_name = "my-unversioned-bucket"
}

resource "awscc_s3_bucket" "fail2" {
  bucket_name = "my-suspended-bucket"
  versioning_configuration = [{
    status = "Suspended"
  }]
}
