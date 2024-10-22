resource "aws_s3_bucket_acl" "example5" {
  bucket = aws_s3_bucket.test.id
  access_control_policy {
    grant {
      grantee {
        id = data.aws_canonical_user_id.current.id
        type = "CanonicalUser"
      }
      permission = "FULL_CONTROL"
    }

    grant {
      grantee {
        id = "xyz"
        type = "CanonicalUser"
      }
      permission = "FULL_CONTROL"
    }
  }
}
