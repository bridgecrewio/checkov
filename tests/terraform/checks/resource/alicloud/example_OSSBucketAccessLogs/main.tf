
resource "alicloud_oss_bucket" "fail" {
  bucket = "bucket-170309-sserule"
  acl    = "private"
}

resource "alicloud_oss_bucket" "pass" {
  bucket = "bucket-170309-logging"

  logging {
    target_bucket = alicloud_oss_bucket.bucket-target.id
    target_prefix = "log/"
  }
}