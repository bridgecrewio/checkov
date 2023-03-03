variable "http_headers" {
  type = list(object({
    num    = number
    values = list
  }))
  default = [{
    "num": 1,
    "protoc": "tcp",
    "values": ["0.0.0.0/0"]
  },
  {
    "num": 2,
    "protoc": "tcp",
    "values": ["0.0.0.0/0"]
  }]
}

variable "aws_vpc" {
  default = true
}