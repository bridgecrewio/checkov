module "firewall" {
  source       = "./modules/firewall"
  network_name = module.vpc.network_name
  fw_name      = "allow-ssh"
}
