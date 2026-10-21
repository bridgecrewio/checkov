module "network" {
  source   = "./modules/vpc"
  vpc_name = "shared-vpc-name"
}

module "firewall" {
  source       = "./modules/firewall"
  network_name = module.network.network_name
}
