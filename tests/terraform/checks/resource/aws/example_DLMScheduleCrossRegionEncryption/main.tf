resource "aws_dlm_lifecycle_policy" "pass" {
  description        = "example DLM lifecycle policy"
  execution_role_arn = aws_iam_role.dlm_lifecycle_role.arn
  state              = "ENABLED"

  policy_details {
    resource_types = ["VOLUME"]

    schedule {
      name = "2 weeks of daily snapshots"

      create_rule {
        interval      = 24
        interval_unit = "HOURS"
        times         = ["23:45"]
      }

      retain_rule {
        count = 14
      }

      tags_to_add = {
        SnapshotCreator = "DLM"
      }

      copy_tags = false

      cross_region_copy_rule {
        target    = "us-west-2"
        encrypted = true
        cmk_arn   = aws_kms_key.dlm_cross_region_copy_cmk.arn
        copy_tags = true
        retain_rule {
          interval      = 30
          interval_unit = "DAYS"
        }
      }
    }

    target_tags = {
      Snapshot = "true"
    }
  }
  tags = {
    test = "failed"
  }
}

resource "aws_dlm_lifecycle_policy" "fail" {
  description        = "example DLM lifecycle policy"
  execution_role_arn = aws_iam_role.dlm_lifecycle_role.arn
  state              = "ENABLED"

  policy_details {
    resource_types = ["VOLUME"]

    schedule {
      name = "2 weeks of daily snapshots"

      create_rule {
        interval      = 24
        interval_unit = "HOURS"
        times         = ["23:45"]
      }

      retain_rule {
        count = 14
      }

      tags_to_add = {
        SnapshotCreator = "DLM"
      }

      copy_tags = false

      cross_region_copy_rule {
        target    = "us-west-2"
        encrypted = true
        cmk_arn   = aws_kms_key.dlm_cross_region_copy_cmk.arn
        copy_tags = true
        retain_rule {
          interval      = 30
          interval_unit = "DAYS"
        }
      }
      cross_region_copy_rule {
        target    = "us-west-2"
        encrypted = false
        cmk_arn   = aws_kms_key.dlm_cross_region_copy_cmk.arn
        copy_tags = true
        retain_rule {
          interval      = 30
          interval_unit = "DAYS"
        }
      }
    }

    target_tags = {
      Snapshot = "true"
    }
  }
  tags = {
    test = "failed"
  }
}

resource "aws_iam_role" "dlm_lifecycle_role" {
  assume_role_policy = ""
}

resource "aws_kms_key" "dlm_cross_region_copy_cmk" {}