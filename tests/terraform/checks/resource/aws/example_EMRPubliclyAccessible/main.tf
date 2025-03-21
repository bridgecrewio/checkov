
resource "aws_emr_block_public_access_configuration" "fail1" {
  block_public_access {
    block_public_acls = false
    ignore_public_acls = false
    restrict_public_buckets = false
  }
}

resource "aws_emr_block_public_access_configuration" "pass" {
  block_public_access {
    block_public_acls = true
    ignore_public_acls = true
    restrict_public_buckets = true
  }
}

resource "aws_emr_block_public_access_configuration" "fail2" {
  block_public_access {
    block_public_acls = false
    ignore_public_acls = true
    restrict_public_buckets = true
  }
}

resource "aws_emr_block_public_access_configuration" "fail3" {
  block_public_access {
    block_public_acls = true
    ignore_public_acls = false
    restrict_public_buckets = true
  }
}

resource "aws_emr_block_public_access_configuration" "fail4" {
  block_public_access {
    block_public_acls = true
    ignore_public_acls = true
    restrict_public_buckets = false
  }
}