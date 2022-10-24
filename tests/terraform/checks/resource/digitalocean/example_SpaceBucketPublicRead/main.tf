
resource "digitalocean_spaces_bucket" "fail" {
  name   = "public_space"
  region = "nyc3"
  acl    = "public-read"
}


resource "digitalocean_spaces_bucket" "pass" {
  name   = "public_space"
  region = "nyc3"
  acl    = "private"
  versioning {
    enabled = true
  }
}


