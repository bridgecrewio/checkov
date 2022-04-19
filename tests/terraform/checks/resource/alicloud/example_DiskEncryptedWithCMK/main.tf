resource "alicloud_disk" "pass" {
  # cn-beijing
  description = "Hello ecs disk."
  category    = "cloud_efficiency"
  size        = "30"
  encrypted   = true
  kms_key_id  = "2a6767f0-a16c-4679-a60f-13bf*****"
  tags = {
    Name = "TerraformTest"
  }
}

resource "alicloud_disk" "unknown" {
  # cn-beijing
  description = "Hello ecs disk."
  category    = "cloud_efficiency"
  size        = "30"
  snapshot_id = "anyvalue"
  tags = {
    Name = "TerraformTest"
  }
}

resource "alicloud_disk" "fail" {
  # cn-beijing
  description = "Hello ecs disk."
  category    = "cloud_efficiency"
  size        = "30"
  tags = {
    Name = "TerraformTest"
  }
}

resource "alicloud_disk" "fail2" {
  # cn-beijing
  description = "Hello ecs disk."
  category    = "cloud_efficiency"
  size        = "30"
  encrypted   = false
  kms_key_id  = "2a6767f0-a16c-4679-a60f-13bf*****"
  tags = {
    Name = "TerraformTest"
  }
}

resource "alicloud_disk" "fail3" {
  # cn-beijing
  description = "Hello ecs disk."
  category    = "cloud_efficiency"
  size        = "30"
  encrypted   = true
  tags = {
    Name = "TerraformTest"
  }
}