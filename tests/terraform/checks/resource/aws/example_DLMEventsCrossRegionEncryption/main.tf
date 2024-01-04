
resource "aws_dlm_lifecycle_policy" "fail" {
  description        = "tf-acc-basic"
  execution_role_arn = aws_iam_role.example.arn

  policy_details {
    policy_type = "EVENT_BASED_POLICY"

    resource_types = []
    target_tags    = {}
    schedule {
      name = "sched"
      create_rule {
        interval = 0
      }
      retain_rule {
        count = 0
      }
    }

    action {
      name = "tf-acc-basic"
      cross_region_copy {
        encryption_configuration {}
      }
    }

    event_source {
      type = "MANAGED_CWE"
      parameters {
        description_regex = "^.*Created for policy: policy-1234567890abcdef0.*$"
        event_type        = "shareSnapshot"
        snapshot_owner    = [data.aws_caller_identity.current.account_id]
      }
    }
  }
}


resource "aws_dlm_lifecycle_policy" "pass" {
  description        = "tf-acc-basic"
  execution_role_arn = aws_iam_role.example.arn

  policy_details {
    policy_type = "EVENT_BASED_POLICY"

    resource_types = []
    target_tags    = {}

    action {
      name = "tf-acc-basic"
      cross_region_copy {
        encryption_configuration {
          cmk_arn    = aws_kms_key.test.arn
          encryption = true
        }
        retain_rule {
          interval      = 15
          interval_unit = "MONTHS"
        }

      }
    }

    event_source {
      type = "MANAGED_CWE"
      parameters {
        description_regex = "^.*Created for policy: policy-1234567890abcdef0.*$"
        event_type        = "shareSnapshot"
        snapshot_owner    = [data.aws_caller_identity.current.account_id]
      }
    }
  }
}

resource "aws_dlm_lifecycle_policy" "fail2" {
  description        = "tf-acc-basic"
  execution_role_arn = aws_iam_role.example.arn

  policy_details {
    policy_type = "EVENT_BASED_POLICY"

    resource_types = []
    target_tags    = {}

    action {
      name = "tf-acc-basic"
      cross_region_copy {
        encryption_configuration {
          cmk_arn    = aws_kms_key.test.arn
          encryption = false
        }
        retain_rule {
          interval      = 15
          interval_unit = "MONTHS"
        }

      }
    }

    event_source {
      type = "MANAGED_CWE"
      parameters {
        description_regex = "^.*Created for policy: policy-1234567890abcdef0.*$"
        event_type        = "shareSnapshot"
        snapshot_owner    = [data.aws_caller_identity.current.account_id]
      }
    }
  }
}

resource "aws_dlm_lifecycle_policy" "unknown" {
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
    }

    target_tags = {
      Snapshot = "true"
    }
  }
}