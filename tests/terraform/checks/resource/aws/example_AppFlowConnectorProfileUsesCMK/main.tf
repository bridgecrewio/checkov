resource "aws_appflow_connector_profile" "fail" {
  name            = "example_profile"
  connector_type  = "Redshift"
  connection_mode = "Public"

  connector_profile_config {

    connector_profile_credentials {
      redshift {
        password = aws_redshift_cluster.example.master_password
        username = aws_redshift_cluster.example.master_username
      }
    }

    connector_profile_properties {
      redshift {
        bucket_name  = aws_s3_bucket.example.name
        database_url = "jdbc:redshift://${aws_redshift_cluster.example.endpoint}/${aws_redshift_cluster.example.database_name}"
        role_arn     = aws_iam_role.example.arn
      }
    }
  }
}

resource "aws_appflow_connector_profile" "pass" {
  name            = "example_profile"
  connector_type  = "Redshift"
  connection_mode = "Public"
  kms_arn = aws_kms_key.example.arn


  connector_profile_config {

    connector_profile_credentials {
      redshift {
        password = aws_redshift_cluster.example.master_password
        username = aws_redshift_cluster.example.master_username
      }
    }

    connector_profile_properties {
      redshift {
        bucket_name  = aws_s3_bucket.example.name
        database_url = "jdbc:redshift://${aws_redshift_cluster.example.endpoint}/${aws_redshift_cluster.example.database_name}"
        role_arn     = aws_iam_role.example.arn
      }
    }
  }
}