resource "alicloud_oss_bucket" "pass" {
  bucket = "bucket_name"

  transfer_acceleration {
    enabled = true
  }
}

resource "alicloud_oss_bucket" "fail" {
  bucket = "bucket_name"

  transfer_acceleration {
    enabled = false
  }
}

resource "alicloud_oss_bucket" "fail2" {
  bucket = "bucket_name"
}
