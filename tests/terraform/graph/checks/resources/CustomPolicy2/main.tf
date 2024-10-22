# if there is a non-resource block, then the pre-fixed version failed with a silent exception
variable "test" {}

resource "aws_sqs_queue" "pass" {
    name          = "pass"
    delay_seconds = 900
}

resource "aws_sqs_queue" "fail" {
    name          = "pass"
    delay_seconds = 0
}
