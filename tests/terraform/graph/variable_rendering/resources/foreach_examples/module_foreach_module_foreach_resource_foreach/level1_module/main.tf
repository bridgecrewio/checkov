module "level2" {
  source   = "../level2_module"
  for_each = var.file_map1_level1

  file_map_level2 = var.file_map2_level1
}