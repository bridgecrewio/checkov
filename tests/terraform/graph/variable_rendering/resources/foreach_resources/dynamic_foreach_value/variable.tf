variable "names_list" {
  default = ["s3-bucket-a", "s3-bucket-b"]
}

variable "names_map" {
  default = {
    a_group       = "eastus"
    another_group = "westus2"
  }
}

variable "number" {
  default = 5
}

variable "number_list" {
  default = ["a", "b", "c"]
}


variable "test" {
  default = "test"
}