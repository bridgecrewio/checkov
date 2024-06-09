resource "aws_iam_role" "MySageMakerRole" {
  name               = "MySageMakerRole"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = {
        Service = "sagemaker.amazonaws.com"
      }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_sagemaker_data_quality_job_definition" "data_quality_job_pass" {
  job_definition_name = "MyDataQualityJob"
  role_arn            = aws_iam_role.MySageMakerRole.arn

  data_quality_app_specification {
    image_uri = "123456789012.dkr.ecr.us-west-2.amazonaws.com/my-image:latest"
  }

  data_quality_job_input {
    endpoint_input {
      endpoint_name = "my-endpoint"
      local_path    = "/opt/ml/processing/input"
    }
  }

  data_quality_job_output_config {
    kms_key_id = "arn:aws:kms:us-west-2:123456789012:key/my-existing-kms-key-id"

    monitoring_outputs {
      s3_output {
        s3_uri        = "s3://my-sagemaker-bucket/output"
        local_path    = "/opt/ml/processing/output"
        s3_upload_mode = "Continuous"
      }
    }
  }

  job_resources {
    cluster_config {
      instance_count  = 1
      instance_type   = "ml.m5.xlarge"
      volume_size_in_gb = 20
      volume_kms_key_id = "arn:aws:kms:us-west-2:123456789012:key/my-existing-kms-key-id"
    }
  }

  stopping_condition {
    max_runtime_in_seconds = 3600
  }
}

resource "aws_sagemaker_data_quality_job_definition" "data_quality_job_fail" {
  job_definition_name = "MyDataQualityJob"
  role_arn            = aws_iam_role.MySageMakerRole.arn

  data_quality_app_specification {
    image_uri = "123456789012.dkr.ecr.us-west-2.amazonaws.com/my-image:latest"
  }

  data_quality_job_input {
    endpoint_input {
      endpoint_name = "my-endpoint"
      local_path    = "/opt/ml/processing/input"
    }
  }

  data_quality_job_output_config {
    monitoring_outputs {
      s3_output {
        s3_uri        = "s3://my-sagemaker-bucket/output"
        local_path    = "/opt/ml/processing/output"
        s3_upload_mode = "Continuous"
      }
    }
  }

  job_resources {
    cluster_config {
      instance_count  = 1
      instance_type   = "ml.m5.xlarge"
      volume_size_in_gb = 20
      volume_kms_key_id = "arn:aws:kms:us-west-2:123456789012:key/my-existing-kms-key-id"
    }
  }

  stopping_condition {
    max_runtime_in_seconds = 3600
  }
}