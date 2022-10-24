resource "aws_s3_bucket" "grant" {
  bucket        = "acme-dev-financials"
  force_destroy = "False"

  grant {
    permissions = ["READ_ACP"]
    type        = "Group"
    uri         = "http://acs.amazonaws.com/groups/global/AllUsers"
  }

  grant {
    id          = "1234567890"
    permissions = ["FULL_CONTROL"]
    type        = "CanonicalUser"
  }

  hosted_zone_id = "EXAMPLE"
  request_payer  = "BucketOwner"

  versioning {
    enabled    = "False"
    mfa_delete = "False"
  }
}
