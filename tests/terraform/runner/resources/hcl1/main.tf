#
# NOTE: This file is not readable by HCL2 due to the dots in the
#       tag name. This is intentional to test HCL1 parsing. The
#       cause of the breakage isn't really important.
#
resource "aws_s3_bucket" "bucket" {
  bucket = "some-bucket-name.example.com"

  # This is the bad setting that will be looked for in the test case
  acl    = "authenticated-read"

  tags {
    linter_override.s3.lint_bucket_acl = "True"
  }
}
