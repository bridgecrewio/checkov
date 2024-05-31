terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "3.2.2"
    }
  }
}

resource "null_resource" "fail1" {
   provisioner "local-exec" {
     command = "echo"
   }
}

resource "null_resource" "pass1" {
}