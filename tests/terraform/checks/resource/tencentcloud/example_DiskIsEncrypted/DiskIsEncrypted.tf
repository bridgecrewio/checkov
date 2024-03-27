## SHOULD PASS: Disk is encrypted
resource "tencentcloud_cbs_storage" "ckv_unittest_pass" {
  storage_name      = "cbs-test"
  storage_type      = "CLOUD_SSD"
  storage_size      = 100
  availability_zone = "ap-guangzhou-3"
  encrypt           = true

  tags = {
    test = "tf"
  }
}

## SHOULD UNKOWN: Set field `snapshot_id`
resource "tencentcloud_cbs_storage" "ckv_unittest_unknown" {
  storage_name      = "cbs-test"
  storage_type      = "CLOUD_SSD"
  storage_size      = 100
  availability_zone = "ap-guangzhou-3"
  snapshot_id       = "anyvalue"

  tags = {
    test = "tf"
  }
}

## SHOULD FAIL: field `encrypt` not set
resource "tencentcloud_cbs_storage" "ckv_unittest_fail" {
  storage_name      = "cbs-test"
  storage_type      = "CLOUD_SSD"
  storage_size      = 100
  availability_zone = "ap-guangzhou-3"

  tags = {
    test = "tf"
  }
}

## SHOULD FAIL: Disk is not encrypted
resource "tencentcloud_cbs_storage" "ckv_unittest_fail_1" {
  storage_name      = "cbs-test"
  storage_type      = "CLOUD_SSD"
  storage_size      = 100
  availability_zone = "ap-guangzhou-3"
  encrypt           = false

  tags = {
    test = "tf"
  }
}