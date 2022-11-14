variable "versioning" {
  type = bool
}

variable "sse" {
  type = list(object({
    kms_master_key_id = string
    sse_algorithm     = string
  }))
  default = [{
    kms_master_key_id = "testkey1"
    sse_algorithm     = "aws:kms"
    },
    {
      kms_master_key_id = "testkey2"
      sse_algorithm     = "aws:notkms"

  }]
}

variable "name" {
  description = "Name of the bucket"
}
