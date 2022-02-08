resource "digitalocean_droplet" "fail" {
  image  = "ubuntu-18-04-x64"
  name   = "web-1"
  region = "nyc2"
  size   = "s-1vcpu-1gb"
}

resource "digitalocean_droplet" "pass" {
  image    = "ubuntu-18-04-x64"
  name     = "web-1"
  region   = "nyc2"
  size     = "s-1vcpu-1gb"
  ssh_keys = [12345, 123456]
}