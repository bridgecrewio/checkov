module "level2" {
  source   = "../level2_module"
  for_each = var.file_map1_level1

  times_to_duplicate_bucket = var.number_of_required_resources_var
}