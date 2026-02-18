resource "awscc_s3_bucket" "pass" {
  bucket_name = "my-secure-bucket"
  
  public_access_block_configuration = {
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }
}

resource "awscc_s3_bucket" "fail" {
  bucket_name = "my-insecure-bucket"
  
  public_access_block_configuration = {
    block_public_acls       = false
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }
}

resource "awscc_s3_bucket" "fail2" {
  bucket_name = "my-default-bucket"
  # No public access block configuration specified
}
