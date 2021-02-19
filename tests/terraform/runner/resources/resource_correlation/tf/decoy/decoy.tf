
# This is a bucket with the same identifiers (type and name) as the bucket above, but for the
# purposes of test_resource_correlation.py's PolicyToBucketVerificationCheck, should not be returned
# because it is in a different terraform context.
resource "aws_s3_bucket" "my_bucket" {
  bucket = "THIS-SHOULD-NOT-BE-FOUND"
}