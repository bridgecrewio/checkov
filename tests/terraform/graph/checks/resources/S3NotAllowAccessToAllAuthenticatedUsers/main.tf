resource "aws_s3_bucket_acl" "fail_1" {
  bucket = "name"
  access_control_policy {
    grant {
      grantee {
        id   = "52b113e7a2f25102679df27bb0ae12b3f85be6"
        type = "CanonicalUser"
      }
      permission = "READ"
    }
    grant {
      grantee {
        type = "Group"
        uri  = "http://acs.amazonaws.com/groups/global/AuthenticatedUsers"
      }
      permission = "READ_ACP"
    }
    owner {
      id = data.aws_canonical_user_id.current.id
    }
  }
}

resource "aws_s3_bucket_acl" "fail_2" {
  bucket = "name"
  access_control_policy {

    grant {
      grantee {
        type = "Group"
        uri  = "http://acs.amazonaws.com/groups/global/AuthenticatedUsers"
      }
      permission = "READ_ACP"
    }
    owner {
      id = data.aws_canonical_user_id.current.id
    }
  }
}

resource "aws_s3_bucket_acl" "pass" {
  bucket = "name"
  access_control_policy {
    grant {
      grantee {
        id   = "52b113e7a2f25102679df27bb0ae12b3f85be6"
        type = "CanonicalUser"
      }
      permission = "READ"
    }
    owner {
      id = data.aws_canonical_user_id.current.id
    }
  }
}
