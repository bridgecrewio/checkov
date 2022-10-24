data "aws_iam_policy_document" "dl_queue_resource" {
  source_json = (
    length(var.resource_reader_arns) > 0
    ? data.aws_iam_policy_document.dl_queue_resource_reader.json
    : ""
  )
}
