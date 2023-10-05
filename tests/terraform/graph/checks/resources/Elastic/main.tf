#disabled-searchengine-authentication --> compliant
#disabled-searchengine-encryption --> compliant
#elastic-search-node-to-node-encryption --> compliant
#elasticsearch-vpc-policy --> compliant
#public-resource-based-policies-elasticsearch --> compliant

provider "aws" {
    region="us-east-1"
}

resource "aws_vpc" "main" {
  cidr_block       = "10.0.0.0/16"
  tags = {
    Name = "elasticsearch-vpc-nov29"
  }
}

resource "aws_subnet" "us-east-1a" {
  vpc_id            = aws_vpc.main.id
  availability_zone = "us-east-1a"
  cidr_block        = "10.0.1.0/24"

  tags = {
    AZ = "elasticsearch-sub1-nov29"
  }
}

resource "aws_subnet" "us-east-1b" {
  vpc_id            = aws_vpc.main.id
  availability_zone = "us-east-1b"
  cidr_block        = "10.0.2.0/24"

  tags = {
    AZ = "elasticsearch-sub2-nov29"
  }
}

resource "aws_security_group" "sample" {
  vpc_id = aws_vpc.main.id
  name = "elasticsearch-sg-nov29"
    ingress {
        cidr_blocks = ["157.48.152.50/32"]
        from_port   = 5432
        to_port     = 5432
        protocol    = "tcp"
    }
}
resource "aws_cognito_user_pool" "pool" {
  name = "comp-mypool"
}

resource "aws_cognito_identity_pool" "main" {
  identity_pool_name               = "comp identity pool"
  allow_unauthenticated_identities = false
  allow_classic_flow               = false
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "comp-domain-terraform"
  user_pool_id = aws_cognito_user_pool.pool.id
}

resource "aws_elasticsearch_domain" "elastic"{
    domain_name = "comp-es-entity"
    elasticsearch_version = "7.10"
    cluster_config {
        instance_type = "t3.small.elasticsearch"
    }
    ebs_options {
        ebs_enabled = true
        volume_size = 10
        volume_type = "gp2"
    }
    vpc_options {
        subnet_ids = ["${aws_subnet.us-east-1a.id}"]
        security_group_ids = ["${aws_security_group.sample.id}"]
    }

    cognito_options {
        enabled          = true ## Changing to False will make the policy non-compliant
        role_arn         = "arn:aws:iam:::role/service-role/CognitoAccessForAmazonOpenSearch"
        user_pool_id     = "${aws_cognito_user_pool.pool.id}"
        identity_pool_id = "${aws_cognito_identity_pool.main.id}"
    }

    node_to_node_encryption {
        enabled = true
    }

    encrypt_at_rest {
        enabled = true
    }

    access_policies= <<POLICY
    {
        "Version": "2012-10-17",
        "Statement": 
        [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS":[ 
                        "arn:aws:iam:::root"
                    ]    
                },
                "Action": [
                    "es:*"
                ],
                "Resource": "arn:aws:es:us-east-1::domain/comp-es-all"
            }
        ]
    }
    POLICY
}

resource "aws_elasticsearch_domain_saml_options" "example" {
  domain_name = aws_elasticsearch_domain.elastic.domain_name
  saml_options {
    enabled = true
    idp {
      entity_id        = "https://example.com"
      metadata_content = file("./saml-metadata.xml")
    }
  }
}