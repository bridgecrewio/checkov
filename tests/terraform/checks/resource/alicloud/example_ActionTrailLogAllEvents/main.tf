resource "alicloud_actiontrail_trail" "pass" {
  trail_name         = "action-trail"
  oss_write_role_arn = "acs:ram::1182725xxxxxxxxxxx"
  oss_bucket_name    = "bucket_name"
  event_rw           = "All"
  trail_region       = "All"
}

#default
resource "alicloud_actiontrail_trail" "fail" {
  trail_name         = "action-trail"
  oss_write_role_arn = "acs:ram::1182725xxxxxxxxxxx"
  oss_bucket_name    = "bucket_name"
  trail_region       = "All"
}

resource "alicloud_actiontrail_trail" "fail2" {
  trail_name         = "action-trail"
  oss_write_role_arn = "acs:ram::1182725xxxxxxxxxxx"
  oss_bucket_name    = "bucket_name"
  event_rw           = "Read"
  trail_region       = "All"
}

terraform {
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "1.162.0"
    }
  }
}
