# pass
resource "aws_comprehend_entity_recognizer" "pass" {
  name = "pass"
  model_kms_key_id = aws_kms_key.test.id

  data_access_role_arn = aws_iam_role.pass.arn

  language_code = "en"
  input_data_config {
    entity_types {
      type = "ENTITY_1"
    }
    entity_types {
      type = "ENTITY_2"
    }

    documents {
      s3_uri = "s3://${aws_s3_bucket.documents.bucket}/${aws_s3_object.documents.id}"
    }

    entity_list {
      s3_uri = "s3://${aws_s3_bucket.entities.bucket}/${aws_s3_object.entities.id}"
    }
  }

  depends_on = [
    aws_iam_role_policy.example
  ]
}

resource "aws_s3_object" "documents" {
  # ...
}

resource "aws_s3_object" "entities" {
  # ...
}

# fail
resource "aws_comprehend_entity_recognizer" "fail" {
  name = "fail"

  data_access_role_arn = aws_iam_role.fail.arn

  language_code = "en"
  input_data_config {
    entity_types {
      type = "ENTITY_1"
    }
    entity_types {
      type = "ENTITY_2"
    }

    documents {
      s3_uri = "s3://${aws_s3_bucket.documents.bucket}/${aws_s3_object.documents.id}"
    }

    entity_list {
      s3_uri = "s3://${aws_s3_bucket.entities.bucket}/${aws_s3_object.entities.id}"
    }
  }

  depends_on = [
    aws_iam_role_policy.example
  ]
}

resource "aws_s3_object" "documents" {
  # ...
}

resource "aws_s3_object" "entities" {
  # ...
}