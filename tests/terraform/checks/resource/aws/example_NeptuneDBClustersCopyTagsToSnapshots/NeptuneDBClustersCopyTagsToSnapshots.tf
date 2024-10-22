## SHOULD PASS: has copy_tags_to_snapshot = true
resource "aws_neptune_cluster" "ckv_unittest_pass" {
  copy_tags_to_snapshot = true
}

## SHOULD FAIL: doens't have copy_tags_to_snapshot
resource "aws_neptune_cluster" "ckv_unittest_fail" {
  copy_tags_to_snapshot = false
}

## SHOULD FAIL: have copy_tags_to_snapshot = false
resource "aws_neptune_cluster" "ckv_unittest2_fail" {
    ## Your test here
}