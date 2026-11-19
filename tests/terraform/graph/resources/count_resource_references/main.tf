resource "aws_s3_bucket" "single" {
  count  = 1
  bucket = "single"
}

resource "aws_s3_bucket" "multi" {
  count  = 3
  bucket = "multi-${count.index}"
}

# literal index into a single-instance resource
resource "aws_s3_bucket_versioning" "single_literal" {
  bucket = aws_s3_bucket.single[0].id
}

# splat on a single-instance resource can only mean that instance
resource "aws_s3_bucket_versioning" "single_splat" {
  bucket = one(aws_s3_bucket.single[*].id)
}

# literal index must bind to exactly that instance
resource "aws_s3_bucket_versioning" "multi_literal" {
  bucket = aws_s3_bucket.multi[2].id
}

# whitespace in the index is only kept inside of a string template
resource "aws_s3_bucket_versioning" "multi_literal_whitespace" {
  bucket = "bucket-${aws_s3_bucket.multi[ 1 ].id}"
}

# the legacy index syntax is only kept inside of a string
resource "aws_s3_bucket_versioning" "multi_legacy_index" {
  bucket = "${aws_s3_bucket.multi.1.id}"
}

resource "aws_s3_bucket_versioning" "multi_decimal_index" {
  bucket = aws_s3_bucket.multi[1.0].id
}

# several literal indexes in one attribute
resource "aws_backup_selection" "multi_literals" {
  resources = [aws_s3_bucket.multi[0].arn, aws_s3_bucket.multi[1].arn]
}

# a splat over several instances is not resolved to a specific instance
resource "aws_s3_bucket_versioning" "multi_splat" {
  bucket = aws_s3_bucket.multi[*].id
}

# function call and legacy splat on a single-instance resource can only mean that instance
resource "aws_s3_bucket_versioning" "single_length" {
  bucket = length(aws_s3_bucket.single)
}

resource "aws_s3_bucket_versioning" "single_legacy_splat" {
  bucket = aws_s3_bucket.single.*.id
}

# the same over several instances is not resolved to a specific instance
resource "aws_s3_bucket_versioning" "multi_length" {
  bucket = length(aws_s3_bucket.multi)
}

# a real reference next to plain text, only the former counts
resource "aws_s3_bucket_versioning" "multi_template" {
  bucket = "${aws_s3_bucket.multi[1].id} and not aws_s3_bucket.multi[2]"
}

# plain text is not a reference
resource "aws_s3_bucket_versioning" "single_text" {
  bucket = "see aws_s3_bucket.single for details"
}

resource "aws_s3_bucket_versioning" "multi_text" {
  bucket = "see aws_s3_bucket.multi[2] for details"
}

resource "aws_s3_bucket_versioning" "single_quoted_in_function" {
  bucket = upper("see aws_s3_bucket.single for details")
}

# reaches the instance through a local, connected by the cross variable edges after rendering
locals {
  single_id = aws_s3_bucket.single[0].id
}

resource "aws_s3_bucket_versioning" "single_through_local" {
  bucket = local.single_id
}

# the same goes for a for_each resource with a single instance
resource "aws_s3_bucket" "for_each_single" {
  for_each = { only = "bucket" }
  bucket   = each.value
}

resource "aws_s3_bucket_versioning" "for_each_single_values" {
  bucket = values(aws_s3_bucket.for_each_single)[0].id
}

resource "aws_s3_bucket_versioning" "for_each_single_depends_on" {
  bucket     = "bucket"
  depends_on = [aws_s3_bucket.for_each_single]
}

resource "aws_s3_bucket_versioning" "for_each_single_text" {
  bucket = "see aws_s3_bucket.for_each_single for details"
}

# quotes and backslashes in a string don't hide the reference next to it
resource "aws_s3_bucket_versioning" "single_trailing_backslash" {
  bucket = format("%s\\", aws_s3_bucket.single[0].id)
}

resource "aws_s3_bucket_versioning" "single_apostrophe" {
  bucket = format("it's %s", aws_s3_bucket.single[0].id)
}

# an escaped template sequence is plain text
resource "aws_s3_bucket_versioning" "single_escaped_template" {
  bucket = "$${aws_s3_bucket.single[0].id}"
}

# a backslash doesn't escape the start of a template sequence
resource "aws_s3_bucket_versioning" "single_backslash_before_template" {
  bucket = format("%s", "C:\\${aws_s3_bucket.single[0].id}")
}

resource "aws_s3_bucket_versioning" "single_backslash_before_escaped_template" {
  bucket = format("%s", "C:\\$${aws_s3_bucket.single[0].id}")
}

# a heredoc in a function keeps its own quotes, only the interpolation is a real reference
resource "aws_s3_bucket_versioning" "single_heredoc_in_function" {
  bucket = trimspace(<<EOT
{"Resource": "${aws_s3_bucket.single[0].id}"}
EOT
  )
}

resource "aws_s3_bucket_versioning" "single_heredoc_in_function_punctuation" {
  bucket = trimspace(<<EOT
see " aws_s3_bucket.single for: details " end
EOT
  )
}

# real code between strings
resource "aws_s3_bucket_versioning" "single_between_strings" {
  bucket = "5" - aws_s3_bucket.single[0].id - "2"
}

resource "aws_s3_bucket_versioning" "single_after_heredoc" {
  bucket = format("%s %s %s", trimspace(<<EOT
see "words" for details
EOT
  ), aws_s3_bucket.single[0].id, "end")
}

resource "aws_s3_bucket_versioning" "single_heredoc_in_function_text" {
  bucket = trimspace(<<EOT
see " aws_s3_bucket.single " for details
EOT
  )
}

# a template directive is an expression as well
resource "aws_s3_bucket_versioning" "single_template_directive" {
  bucket = "%{ for b in aws_s3_bucket.single }${b.id}%{ endfor }"
}

resource "aws_s3_bucket_versioning" "single_template_directive_object" {
  bucket = "%{ if length({ a = true }) > 0 && length(aws_s3_bucket.single) > 0 }yes%{ endif }"
}

# the literal index doesn't exist, the splat can only mean the single instance
resource "aws_s3_bucket_versioning" "single_literal_and_splat" {
  bucket = try(aws_s3_bucket.single[1].id, one(aws_s3_bucket.single[*].id))
}
