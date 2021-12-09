resource "digitalocean_firewall" "fail" {
  name = "ssh-from-world"

  droplet_ids = [digitalocean_droplet.web.id]

  inbound_rule {
    protocol         = "http"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
}

resource "digitalocean_firewall" "pass" {
  name = "ssh-from-world"

  droplet_ids = [digitalocean_droplet.web.id]

  inbound_rule {
    protocol         = "http"
    port_range       = "80"
    source_addresses = ["10.0.0.0/16"]
  }
}