resource "aws_fsx_s3_access_point_attachment" "pass" {
  name = "example-attachment"
  type = "OPENZFS"

  openzfs_configuration {
    volume_id = "fsvol-1234567890"

    file_system_identity {
      type = "POSIX"

      posix_user {
        uid = 1001
        gid = 1001
      }
    }
  }

  s3_access_point {
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect   = "Allow"
          Principal = {
            AWS = "*"
          }
          Action   = "s3:GetObject"
          Resource = "arn:aws:s3:::my-bucket/*"
        }
      ]
    })
  }
}

resource "aws_fsx_s3_access_point_attachment" "fail" {
  name = "example-attachment"
  type = "OPENZFS"

  openzfs_configuration {
    volume_id = "fsvol-1234567890"

    file_system_identity {
      type = "POSIX"

      posix_user {
        uid = 1001
        gid = 1001
      }
    }
  }
}
