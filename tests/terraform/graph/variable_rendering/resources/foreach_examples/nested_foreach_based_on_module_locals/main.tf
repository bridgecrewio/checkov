locals {
  groups = {
      "blue" = "blue"
      "green" = "green"
  }
  files_map1 = {
    "test1" = "test1"
    "test2" = "test2"
  }
}

# Expected resources:
#    module.files["blue"].aws_s3_bucket_object.this_file["test1.txt"]
#    module.files["blue"].aws_s3_bucket_object.this_file["test2.txt"]
#    module.files["green"].aws_s3_bucket_object.this_file["test1.txt"]
#    module.files["green"].aws_s3_bucket_object.this_file["test2.txt"]

module "files" {
  source   = "./s3_files"
  for_each = local.groups
  file_map = local.files_map1
}
