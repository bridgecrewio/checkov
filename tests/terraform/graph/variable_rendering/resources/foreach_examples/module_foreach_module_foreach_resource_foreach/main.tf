locals {
  groups = {
    "blue"  = "blue"
    "green" = "green"
  }
  files_map1 = {
    "test1.txt" = "test1.txt"
    "test2.txt" = "test2.txt"
  }
  files_map2 = {
    "test3.txt" = "test3.txt"
    "test4.txt" = "test4.txt"
  }
}

# Expected resources:
#    module.level1["blue"].module.level2["test1.txt"].aws_s3_bucket_object.this_file["test3.txt"]
#    module.level1["blue"].module.level2["test1.txt"].aws_s3_bucket_object.this_file["test4.txt"]
#    module.level1["blue"].module.level2["test2.txt"].aws_s3_bucket_object.this_file["test3.txt"]
#    module.level1["blue"].module.level2["test2.txt"].aws_s3_bucket_object.this_file["test4.txt"]
#    module.level1["green"].module.level2["test1.txt"].aws_s3_bucket_object.this_file["test3.txt"]
#    module.level1["green"].module.level2["test1.txt"].aws_s3_bucket_object.this_file["test4.txt"]
#    module.level1["green"].module.level2["test2.txt"].aws_s3_bucket_object.this_file["test3.txt"]
#    module.level1["green"].module.level2["test2.txt"].aws_s3_bucket_object.this_file["test4.txt"]

module "level1" {
  source   = "./level1_module"
  for_each = local.groups

  file_map1_level1 = local.files_map1
  file_map2_level1 = local.files_map2
}
