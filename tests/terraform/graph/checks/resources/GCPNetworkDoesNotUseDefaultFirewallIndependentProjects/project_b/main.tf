module "standalone_network" {
  source   = "./modules/vpc"
  vpc_name = "shared-vpc-name"
}
