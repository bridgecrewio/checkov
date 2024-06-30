variable "test_list" {
  bucket = ["a", "b"]
}

variable "test_dict" {
  bucket = {
    key1 = "a",
    key2 = "b"
  }
}

variable "test_count" {
  bucket = 2
}