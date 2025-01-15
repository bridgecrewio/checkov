
resource "aws_codegurureviewer_repository_association" "pass" {
  repository {
    codecommit {
      name = "repository_name"
    }
  }
  kms_key_details {
    encryption_option = "CUSTOMER_MANAGED_CMK"
    kms_key_id        = "aws_kms_key.example.key_id"
  }
}

resource "aws_codegurureviewer_repository_association" "ckv_unittest_fail_no_encryption_option" {
  repository {
    codecommit {
      name = "repository_name"
    }
  }
  kms_key_details {
    kms_key_id        = "aws_kms_key.example.key_id"
  }
}


resource "aws_codegurureviewer_repository_association" "ckv_unittest_fail_no_kms_key_details" {
  repository {
    codecommit {
      name = "repository_name"
    }
  }
}

resource "aws_codegurureviewer_repository_association" "ckv_unittest_fail_encryption_option_OWNED" {
  repository {
    codecommit {
      name = "repository_name"
    }
  }
  kms_key_details {
    encryption_option = "AWS_OWNED_CMK"
    kms_key_id        = "aws_kms_key.example.key_id"
  }
}
