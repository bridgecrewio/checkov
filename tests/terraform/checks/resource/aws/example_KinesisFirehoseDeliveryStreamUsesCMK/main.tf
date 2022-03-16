resource "aws_kinesis_firehose_delivery_stream" "ignore" {
  name        = "terraform-kinesis-firehose-test-stream"
  destination = "s3"

kinesis_source_configuration {
  kinesis_stream_arn = ""
  role_arn           = ""
}

  # server_side_encryption {
    # enabled=true #default is false
    # key_type="CUSTOMER_MANAGED_CMK"
    # key_arn=aws_kms_kmy.example.arn
  # }
  tags = {
    test = "failed"
  }
}


# fails default is off
resource "aws_kinesis_firehose_delivery_stream" "fail" {
  name        = "terraform-kinesis-firehose-test-stream"
  destination = "s3"

  s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.bucket.arn
  }

  # server_side_encryption {
    # enabled=true #default is false
    # key_type="CUSTOMER_MANAGED_CMK"
    # key_arn=aws_kms_kmy.example.arn
  # }
  tags = {
    test = "failed"
  }
}

#not enabled
resource "aws_kinesis_firehose_delivery_stream" "fail2" {
  name        = "terraform-kinesis-firehose-test-stream"
  destination = "s3"

  s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.bucket.arn
  }

   server_side_encryption {
    # enabled=true #default is false
    # key_type="CUSTOMER_MANAGED_CMK"
    # key_arn=aws_kms_kmy.example.arn
   }
  tags = {
    test = "failed"
  }
}

#key_type not set
resource "aws_kinesis_firehose_delivery_stream" "fail3" {
  name        = "terraform-kinesis-firehose-test-stream"
  destination = "s3"

  s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.bucket.arn
  }

   server_side_encryption {
     enabled=true
     key_arn = ""
   }
  tags = {
    test = "failed"
  }
}

#wrong type
resource "aws_kinesis_firehose_delivery_stream" "fail4" {
  name        = "terraform-kinesis-firehose-test-stream"
  destination = "s3"

  s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.bucket.arn
  }

   server_side_encryption {
     enabled=true
     key_type = "AWS_OWNED_CMK"
     key_arn = ""
   }
  tags = {
    test = "failed"
  }
}

#no key
resource "aws_kinesis_firehose_delivery_stream" "fail5" {
  name        = "terraform-kinesis-firehose-test-stream"
  destination = "s3"

  s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.bucket.arn
  }

   server_side_encryption {
     enabled=true
     key_type = "CUSTOMER_MANAGED_CMK"
     key_arn = ""
   }
  tags = {
    test = "failed"
  }
}

#missing key
resource "aws_kinesis_firehose_delivery_stream" "fail6" {
  name        = "terraform-kinesis-firehose-test-stream"
  destination = "s3"

  s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.bucket.arn
  }

   server_side_encryption {
     enabled=true
     key_type = "CUSTOMER_MANAGED_CMK"
   }
  tags = {
    test = "failed"
  }
}

resource "aws_kinesis_firehose_delivery_stream" "pass" {
  name        = "terraform-kinesis-firehose-test-stream"
  destination = "s3"

  s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.bucket.arn
  }

   server_side_encryption {
     enabled=true #default is false
     key_type = "CUSTOMER_MANAGED_CMK"
     key_arn = aws_kms_key.example.arn
   }
  tags = {
    test = "failed"
  }
}