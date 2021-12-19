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

resource "digitalocean_firewall" "droplet" {
  name = "http-from-droplet"

  droplet_ids = [digitalocean_droplet.web.id]

  inbound_rule {
    protocol           = "http"
    port_range         = "80"
    source_droplet_ids = ["var.cluster_droplet_ids"]
  }
}
