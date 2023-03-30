from textwrap import dedent

from checkov.common.output.ai import OpenAi


def test_parse_completion_response():
    # given
    content = dedent(
        """\
        The given code creates an AWS RDS instance with MySQL engine version 5.7, with a 10GB allocated storage, and a retention period of 7 days. However, it does not specify any encryption settings for the RDS instance, which violates the checkov policy 'Ensure all data stored in the RDS is securely encrypted at rest'. This means that sensitive data stored in the RDS instance may be vulnerable to unauthorized access or theft.
        
        To fix this, we need to enable encryption for the RDS instance. AWS RDS provides two options for encryption: AWS managed encryption and customer-managed encryption. In this case, we will use AWS managed encryption, which is the simpler option.
        
        To enable AWS managed encryption, we need to add the following block to the resource definition:
        
        ```
          storage_encrypted = true
          kms_key_id        = "alias/aws/rds"
        ```
        
        The `storage_encrypted` parameter enables encryption for the RDS instance, and the `kms_key_id` parameter specifies the AWS KMS key to use for encryption. In this case, we are using the default AWS RDS KMS key.
        
        The updated code with encryption enabled will look like this:
        
        ```
        resource "aws_db_instance" "pass" {
          allocated_storage      = 10
          db_name                = "mydb"
          engine                 = "mysql"
          engine_version         = "5.7"
          instance_class         = "db.t3.micro"
          username               = "foo"
          password               = "foobarbaz"
          parameter_group_name   = "default.mysql5.7"
          skip_final_snapshot    = true
          copy_tags_to_snapshot  = true
          backup_retention_period = 7
        
          storage_encrypted = true
          kms_key_id        = "alias/aws/rds"
        }
        ``` 
        
        With this change, the RDS instance will be encrypted at rest, and will comply with the checkov policy.
        """
    )

    # when
    details = OpenAi()._parse_completion_response(completion_content=content)

    # then
    assert details == [
        "The following text is AI generated and should be treated as a suggestion.",
        "",
        "The given code creates an AWS RDS instance with MySQL engine version 5.7, with a 10GB allocated storage, and a retention period of 7 days.",
        "However, it does not specify any encryption settings for the RDS instance, which violates the checkov policy 'Ensure all data stored in the RDS is securely encrypted at rest'.",
        "This means that sensitive data stored in the RDS instance may be vulnerable to unauthorized access or theft.",
        "",
        "To fix this, we need to enable encryption for the RDS instance.",
        "AWS RDS provides two options for encryption: AWS managed encryption and customer-managed encryption.",
        "In this case, we will use AWS managed encryption, which is the simpler option.",
        "",
        "To enable AWS managed encryption, we need to add the following block to the resource definition:",
        "",
        "  storage_encrypted = true",
        '  kms_key_id        = "alias/aws/rds"',
        "",
        "The `storage_encrypted` parameter enables encryption for the RDS instance, and the `kms_key_id` parameter specifies the AWS KMS key to use for encryption.",
        "In this case, we are using the default AWS RDS KMS key.",
        "",
        "The updated code with encryption enabled will look like this:",
        "",
        'resource "aws_db_instance" "pass" {',
        "  allocated_storage      = 10",
        '  db_name                = "mydb"',
        '  engine                 = "mysql"',
        '  engine_version         = "5.7"',
        '  instance_class         = "db.t3.micro"',
        '  username               = "foo"',
        '  password               = "foobarbaz"',
        '  parameter_group_name   = "default.mysql5.7"',
        "  skip_final_snapshot    = true",
        "  copy_tags_to_snapshot  = true",
        "  backup_retention_period = 7",
        "",
        "  storage_encrypted = true",
        '  kms_key_id        = "alias/aws/rds"',
        "}",
        "",
        "With this change, the RDS instance will be encrypted at rest, and will comply with the checkov policy.",
    ]
