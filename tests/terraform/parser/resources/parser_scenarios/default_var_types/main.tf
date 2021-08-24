variable "map_with_default" {
  type = map(string)
  default = {x = "123"}
}

variable "map_without_default" {
  type = map(string)
}

variable "map_with_default_no_type" {
  type = map
  default = {x = "123"}
}

variable "map_without_default_no_type" {
  type = map
}

variable "list_with_default" {
  type = list(string)
  default = ["123"]
}

variable "list_without_default" {
  type = list(string)
}


resource "google_compute_instance" "a" {
  metadata = merge(var.map_with_default, {block-project-ssh-keys = true})
}

resource "google_compute_instance" "b" {
  metadata = merge(var.map_without_default, {block-project-ssh-keys = true})
}

resource "google_compute_instance" "c" {
  metadata = merge(var.map_with_default_no_type, {block-project-ssh-keys = true})
}

resource "google_compute_instance" "d" {
  metadata = merge(var.map_without_default_no_type, {block-project-ssh-keys = true})
}

resource "google_compute_instance" "e" {
  metadata = concat(var.list_with_default, ["xyz"])
}

resource "google_compute_instance" "f" {
  metadata = concat(var.list_without_default, ["xyz"])
}
