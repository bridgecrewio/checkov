## SHOULD PASS: iam_database_authentication_enabled set to true
resource "aws_neptune_cluster" "ckv_unittest_pass" {
    ## Your test here
  cluster_identifier = "bla"
  iam_database_authentication_enabled = true
}

## SHOULD FAIL: iam_database_authentication_enabled set to false
resource "aws_neptune_cluster" "ckv_unittest_fail" {
    ## Your test here
  cluster_identifier = "bla_fail"
  iam_database_authentication_enabled = false
}


## SHOULD FAIL: iam_database_authentication_enabled doesn't exist
resource "aws_neptune_cluster" "ckv_unittest2_fail" {
    ## Your test here
  cluster_identifier = "bla_fail"
}