terraform {
  backend "remote" {
    organization = "acme-sre"

    workspaces {
      name = "aws_pairs-acme"
    }
  }
}