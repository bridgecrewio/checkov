
module "m" {
  count = 1
  # checkov:skip=CKV2_AWS_6: ADD REASON
  source = "../mod_ref"
}