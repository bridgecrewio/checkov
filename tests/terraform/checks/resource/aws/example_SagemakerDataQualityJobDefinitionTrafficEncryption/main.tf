provider "aws" {
  region = "us-west-2"
}

resource "aws_sagemaker_data_quality_job_definition" "data_quality_job_pass" {
  job_definition_name = "MyDataQualityJobDefinition"

  data_quality_baseline_config {
    baselining_job_name = "MyBaselineJob"
  }

  data_quality_app_specification {
    image_uri = "123456789012.dkr.ecr.us-west-2.amazonaws.com/my-custom-image:latest"
  }

  data_quality_job_input {
    endpoint_input {
      endpoint_name = "MyEndpoint"
      local_path    = "/opt/ml/processing/input"
    }
  }

  data_quality_job_output_config {
    monitoring_outputs {
      s3_output {
        s3_uri        = "s3://my-bucket/output/"
        local_path    = "/opt/ml/processing/output"
        s3_upload_mode = "EndOfJob"
      }
    }
  }

  role_arn = "arn:aws:iam::123456789012:role/service-role/AmazonSageMaker-ExecutionRole-20200601T123456"

  network_config {
    enable_inter_container_traffic_encryption = true
  }

  stopping_condition {
    max_runtime_in_seconds = 3600
  }
}

resource "aws_sagemaker_data_quality_job_definition" "data_quality_job_fail_1" {
  job_definition_name = "MyDataQualityJobDefinition"

  data_quality_baseline_config {
    baselining_job_name = "MyBaselineJob"
  }

  data_quality_app_specification {
    image_uri = "123456789012.dkr.ecr.us-west-2.amazonaws.com/my-custom-image:latest"
  }

  data_quality_job_input {
    endpoint_input {
      endpoint_name = "MyEndpoint"
      local_path    = "/opt/ml/processing/input"
    }
  }

  data_quality_job_output_config {
    monitoring_outputs {
      s3_output {
        s3_uri        = "s3://my-bucket/output/"
        local_path    = "/opt/ml/processing/output"
        s3_upload_mode = "EndOfJob"
      }
    }
  }

  role_arn = "arn:aws:iam::123456789012:role/service-role/AmazonSageMaker-ExecutionRole-20200601T123456"

  network_config {
    enable_inter_container_traffic_encryption = false
  }

  stopping_condition {
    max_runtime_in_seconds = 3600
  }
}

resource "aws_sagemaker_data_quality_job_definition" "data_quality_job_fail_2" {
  job_definition_name = "MyDataQualityJobDefinition"

  data_quality_baseline_config {
    baselining_job_name = "MyBaselineJob"
  }

  data_quality_app_specification {
    image_uri = "123456789012.dkr.ecr.us-west-2.amazonaws.com/my-custom-image:latest"
  }

  data_quality_job_input {
    endpoint_input {
      endpoint_name = "MyEndpoint"
      local_path    = "/opt/ml/processing/input"
    }
  }

  data_quality_job_output_config {
    monitoring_outputs {
      s3_output {
        s3_uri        = "s3://my-bucket/output/"
        local_path    = "/opt/ml/processing/output"
        s3_upload_mode = "EndOfJob"
      }
    }
  }

  role_arn = "arn:aws:iam::123456789012:role/service-role/AmazonSageMaker-ExecutionRole-20200601T123456"

  stopping_condition {
    max_runtime_in_seconds = 3600
  }
}