
resource "aws_cloudtrail_event_data_store" "pass" {
  name = "pike-data-store"
  kms_key_id=aws_kms_key.pike.arn
}
resource "aws_cloudtrail_event_data_store" "fail" {
  name = "example-event-data-store"
}
resource "aws_cloudtrail_event_data_store" "fail2" {
  name = "example-event-data-store"
  kms_key_id=""
}