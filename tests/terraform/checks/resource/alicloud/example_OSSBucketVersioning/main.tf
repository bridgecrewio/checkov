resource "alicloud_oss_bucket" "pass" {
  bucket = "bucket-170309-versioning"
  acl    = "private"

  versioning {
    status = "Enabled"
  }
}

resource "alicloud_oss_bucket" "fail" {
  bucket = "bucket-170309-versioning"
  acl    = "private"
}

resource "alicloud_oss_bucket" "fail2" {
  bucket = "bucket-170309-versioning"
  acl    = "private"

  versioning {
    status = "Suspended"
  }
}
