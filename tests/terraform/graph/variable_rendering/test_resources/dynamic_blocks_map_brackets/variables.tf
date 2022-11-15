variable "http_headers" {
  type = list(object({
    num    = number
    values = string
  }))
  default = [{
    "num": 1,
    "protoc": "tcp",
    "values": "10.0.0.1/32"
  },
  {
    "num": 2,
    "protoc": "tcp",
    "values": "10.0.0.2/32"
  }]
}

variable "aws_vpc" {
  default = true
}