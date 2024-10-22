variable "foreach_map" {
  default = {
    bucket_a: "us-west-2",
    bucket_b: "us-east-2"
  }
}

variable "foreach_list" {
  default = ["bucket_a", "bucket_b"]
}