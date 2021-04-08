variable "create_vpc" {
  description = "Controls if VPC should be created (it affects almost all resources)"
  type        = bool
  default     = true
}

variable "name" {
  description = "Name to be used on all the resources as identifier"
  default     = ""
}

variable "cidr" {
  description = "The CIDR block for the VPC. Default value is a valid CIDR, but not acceptable by AWS and should be overridden"
  default     = "0.0.0.0/0"
}

variable "assign_generated_ipv6_cidr_block" {
  description = "Requests an Amazon-provided IPv6 CIDR block with a /56 prefix length for the VPC. You cannot specify the range of IP addresses, or the size of the CIDR block"
  type        = bool
  default     = false
}

variable "secondary_cidr_blocks" {
  description = "List of secondary CIDR blocks to associate with the VPC to extend the IP Address pool"
  type        = list(string)
  default     = []
}

variable "instance_tenancy" {
  description = "A tenancy option for instances launched into the VPC"
  type        = string
  default     = "default"
}

variable "public_subnet_suffix" {
  description = "Suffix to append to public subnets name"
  type        = string
  default     = "public"
}

variable "private_subnet_suffix" {
  description = "Suffix to append to private subnets name"
  type        = string
  default     = "private"
}

variable "intra_subnet_suffix" {
  description = "Suffix to append to intra subnets name"
  type        = string
  default     = "intra"
}

variable "database_subnet_suffix" {
  description = "Suffix to append to database subnets name"
  type        = string
  default     = "db"
}

variable "redshift_subnet_suffix" {
  description = "Suffix to append to redshift subnets name"
  type        = string
  default     = "redshift"
}

variable "elasticache_subnet_suffix" {
  description = "Suffix to append to elasticache subnets name"
  type        = string
  default     = "elasticache"
}

variable "public_subnets" {
  description = "A list of public subnets inside the VPC"
  type        = list(string)
  default     = []
}

variable "private_subnets" {
  description = "A list of private subnets inside the VPC"
  type        = list(string)
  default     = []
}

variable "database_subnets" {
  description = "A list of database subnets"
  type        = list(string)
  default     = []
}

variable "redshift_subnets" {
  description = "A list of redshift subnets"
  type        = list(string)
  default     = []
}

variable "elasticache_subnets" {
  description = "A list of elasticache subnets"
  type        = list(string)
  default     = []
}

variable "intra_subnets" {
  description = "A list of intra subnets"
  type        = list(string)
  default     = []
}

variable "create_database_subnet_route_table" {
  description = "Controls if separate route table for database should be created"
  type        = bool
  default     = false
}

variable "create_redshift_subnet_route_table" {
  description = "Controls if separate route table for redshift should be created"
  type        = bool
  default     = false
}

variable "enable_public_redshift" {
  description = "Controls if redshift should have public routing table"
  type        = bool
  default     = false
}

variable "create_elasticache_subnet_route_table" {
  description = "Controls if separate route table for elasticache should be created"
  type        = bool
  default     = false
}

variable "create_database_subnet_group" {
  description = "Controls if database subnet group should be created"
  type        = bool
  default     = true
}

variable "create_elasticache_subnet_group" {
  description = "Controls if elasticache subnet group should be created"
  type        = bool
  default     = true
}

variable "create_redshift_subnet_group" {
  description = "Controls if redshift subnet group should be created"
  type        = bool
  default     = true
}

variable "create_database_internet_gateway_route" {
  description = "Controls if an internet gateway route for public database access should be created"
  type        = bool
  default     = false
}

variable "create_database_nat_gateway_route" {
  description = "Controls if a nat gateway route should be created to give internet access to the database subnets"
  type        = bool
  default     = false
}

variable "azs" {
  description = "A list of availability zones in the region"
  type        = list(string)
  default     = []
}

variable "enable_dns_hostnames" {
  description = "Should be true to enable DNS hostnames in the VPC"
  type        = bool
  default     = false
}

variable "enable_dns_support" {
  description = "Should be true to enable DNS support in the VPC"
  type        = bool
  default     = true
}

variable "enable_nat_gateway" {
  description = "Should be true if you want to provision NAT Gateways for each of your private networks"
  type        = bool
  default     = false
}

variable "single_nat_gateway" {
  description = "Should be true if you want to provision a single shared NAT Gateway across all of your private networks"
  type        = bool
  default     = false
}

variable "one_nat_gateway_per_az" {
  description = "Should be true if you want only one NAT Gateway per availability zone. Requires `var.azs` to be set, and the number of `public_subnets` created to be greater than or equal to the number of availability zones specified in `var.azs`."
  type        = bool
  default     = false
}

variable "reuse_nat_ips" {
  description = "Should be true if you don't want EIPs to be created for your NAT Gateways and will instead pass them in via the 'external_nat_ip_ids' variable"
  type        = bool
  default     = false
}

variable "external_nat_ip_ids" {
  description = "List of EIP IDs to be assigned to the NAT Gateways (used in combination with reuse_nat_ips)"
  type        = list(string)
  default     = []
}

variable "enable_dynamodb_endpoint" {
  description = "Should be true if you want to provision a DynamoDB endpoint to the VPC"
  type        = bool
  default     = false
}

variable "enable_s3_endpoint" {
  description = "Should be true if you want to provision an S3 endpoint to the VPC"
  type        = bool
  default     = false
}

variable "enable_sqs_endpoint" {
  description = "Should be true if you want to provision an SQS endpoint to the VPC"
  default     = false
}

variable "sqs_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for SQS endpoint"
  default     = []
}

variable "sqs_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for SQS endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  default     = []
}

variable "sqs_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for SQS endpoint"
  default     = false
}

variable "enable_ssm_endpoint" {
  description = "Should be true if you want to provision an SSM endpoint to the VPC"
  type        = bool
  default     = false
}

variable "ssm_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for SSM endpoint"
  type        = list(string)
  default     = []
}

variable "ssm_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for SSM endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "ssm_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for SSM endpoint"
  type        = bool
  default     = false
}

variable "enable_ssmmessages_endpoint" {
  description = "Should be true if you want to provision a SSMMESSAGES endpoint to the VPC"
  type        = bool
  default     = false
}

variable "enable_apigw_endpoint" {
  description = "Should be true if you want to provision an api gateway endpoint to the VPC"
  type        = bool
  default     = false
}

variable "apigw_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for API GW  endpoint"
  type        = list(string)
  default     = []
}

variable "apigw_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for API GW endpoint"
  type        = bool
  default     = false
}

variable "apigw_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for API GW endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "ssmmessages_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for SSMMESSAGES endpoint"
  type        = list(string)
  default     = []
}

variable "ssmmessages_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for SSMMESSAGES endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "ssmmessages_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for SSMMESSAGES endpoint"
  type        = bool
  default     = false
}

variable "enable_ec2_endpoint" {
  description = "Should be true if you want to provision an EC2 endpoint to the VPC"
  type        = bool
  default     = false
}

variable "ec2_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for EC2 endpoint"
  type        = list(string)
  default     = []
}

variable "ec2_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for EC2 endpoint"
  type        = bool
  default     = false
}

variable "ec2_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for EC2 endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "enable_ec2messages_endpoint" {
  description = "Should be true if you want to provision an EC2MESSAGES endpoint to the VPC"
  type        = bool
  default     = false
}

variable "ec2messages_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for EC2MESSAGES endpoint"
  type        = list(string)
  default     = []
}

variable "ec2messages_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for EC2MESSAGES endpoint"
  type        = bool
  default     = false
}

variable "ec2messages_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for EC2MESSAGES endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "enable_ecr_api_endpoint" {
  description = "Should be true if you want to provision an ecr api endpoint to the VPC"
  type        = bool
  default     = false
}

variable "ecr_api_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for ECR api endpoint. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "ecr_api_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for ECR API endpoint"
  type        = bool
  default     = false
}

variable "ecr_api_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for ECR API endpoint"
  type        = list(string)
  default     = []
}

variable "enable_ecr_dkr_endpoint" {
  description = "Should be true if you want to provision an ecr dkr endpoint to the VPC"
  type        = bool
  default     = false
}

variable "ecr_dkr_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for ECR dkr endpoint. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "ecr_dkr_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for ECR DKR endpoint"
  type        = bool
  default     = false
}

variable "ecr_dkr_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for ECR DKR endpoint"
  type        = list(string)
  default     = []
}

variable "enable_kms_endpoint" {
  description = "Should be true if you want to provision a KMS endpoint to the VPC"
  type        = bool
  default     = false
}

variable "kms_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for KMS endpoint"
  type        = list(string)
  default     = []
}

variable "kms_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for KMS endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "kms_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for KMS endpoint"
  type        = bool
  default     = false
}

variable "enable_ecs_endpoint" {
  description = "Should be true if you want to provision a ECS endpoint to the VPC"
  type        = bool
  default     = false
}

variable "ecs_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for ECS endpoint"
  type        = list(string)
  default     = []
}

variable "ecs_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for ECS endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "ecs_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for ECS endpoint"
  type        = bool
  default     = false
}

variable "enable_ecs_agent_endpoint" {
  description = "Should be true if you want to provision a ECS Agent endpoint to the VPC"
  type        = bool
  default     = false
}

variable "ecs_agent_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for ECS Agent endpoint"
  type        = list(string)
  default     = []
}

variable "ecs_agent_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for ECS Agent endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "ecs_agent_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for ECS Agent endpoint"
  type        = bool
  default     = false
}

variable "enable_ecs_telemetry_endpoint" {
  description = "Should be true if you want to provision a ECS Telemetry endpoint to the VPC"
  type        = bool
  default     = false
}

variable "ecs_telemetry_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for ECS Telemetry endpoint"
  type        = list(string)
  default     = []
}

variable "ecs_telemetry_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for ECS Telemetry endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "ecs_telemetry_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for ECS Telemetry endpoint"
  type        = bool
  default     = false
}

variable "enable_sns_endpoint" {
  description = "Should be true if you want to provision a SNS endpoint to the VPC"
  type        = bool
  default     = false
}

variable "sns_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for SNS endpoint"
  type        = list(string)
  default     = []
}

variable "sns_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for SNS endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "sns_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for SNS endpoint"
  type        = bool
  default     = false
}

variable "enable_monitoring_endpoint" {
  description = "Should be true if you want to provision a CloudWatch Monitoring endpoint to the VPC"
  type        = bool
  default     = false
}

variable "monitoring_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for CloudWatch Monitoring endpoint"
  type        = list(string)
  default     = []
}

variable "monitoring_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for CloudWatch Monitoring endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "monitoring_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for CloudWatch Monitoring endpoint"
  type        = bool
  default     = false
}

variable "enable_elasticloadbalancing_endpoint" {
  description = "Should be true if you want to provision a Elastic Load Balancing endpoint to the VPC"
  type        = bool
  default     = false
}

variable "elasticloadbalancing_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for Elastic Load Balancing endpoint"
  type        = list(string)
  default     = []
}

variable "elasticloadbalancing_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for Elastic Load Balancing endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "elasticloadbalancing_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for Elastic Load Balancing endpoint"
  type        = bool
  default     = false
}

variable "enable_events_endpoint" {
  description = "Should be true if you want to provision a CloudWatch Events endpoint to the VPC"
  type        = bool
  default     = false
}

variable "events_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for CloudWatch Events endpoint"
  type        = list(string)
  default     = []
}

variable "events_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for CloudWatch Events endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "events_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for CloudWatch Events endpoint"
  type        = bool
  default     = false
}

variable "enable_logs_endpoint" {
  description = "Should be true if you want to provision a CloudWatch Logs endpoint to the VPC"
  type        = bool
  default     = false
}

variable "logs_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for CloudWatch Logs endpoint"
  type        = list(string)
  default     = []
}

variable "logs_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for CloudWatch Logs endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "logs_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for CloudWatch Logs endpoint"
  type        = bool
  default     = false
}

variable "enable_cloudtrail_endpoint" {
  description = "Should be true if you want to provision a CloudTrail endpoint to the VPC"
  type        = bool
  default     = false
}

variable "cloudtrail_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for CloudTrail endpoint"
  type        = list(string)
  default     = []
}

variable "cloudtrail_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for CloudTrail endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  type        = list(string)
  default     = []
}

variable "cloudtrail_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for CloudTrail endpoint"
  type        = bool
  default     = false
}

variable "map_public_ip_on_launch" {
  description = "Should be false if you do not want to auto-assign public IP on launch"
  type        = bool
  default     = true
}

variable "enable_vpn_gateway" {
  description = "Should be true if you want to create a new VPN Gateway resource and attach it to the VPC"
  type        = bool
  default     = false
}

variable "vpn_gateway_id" {
  description = "ID of VPN Gateway to attach to the VPC"
  default     = ""
}

variable "amazon_side_asn" {
  description = "The Autonomous System Number (ASN) for the Amazon side of the gateway. By default the virtual private gateway is created with the current default Amazon ASN."
  default     = "64512"
}

variable "propagate_private_route_tables_vgw" {
  description = "Should be true if you want route table propagation"
  type        = bool
  default     = false
}

variable "propagate_public_route_tables_vgw" {
  description = "Should be true if you want route table propagation"
  type        = bool
  default     = false
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}

variable "vpc_tags" {
  description = "Additional tags for the VPC"
  type        = map(string)
  default     = {}
}

variable "igw_tags" {
  description = "Additional tags for the internet gateway"
  type        = map(string)
  default     = {}
}

variable "public_subnet_tags" {
  description = "Additional tags for the public subnets"
  type        = map(string)
  default     = {}
}

variable "private_subnet_tags" {
  description = "Additional tags for the private subnets"
  type        = map(string)
  default     = {}
}

variable "public_route_table_tags" {
  description = "Additional tags for the public route tables"
  type        = map(string)
  default     = {}
}

variable "private_route_table_tags" {
  description = "Additional tags for the private route tables"
  type        = map(string)
  default     = {}
}

variable "database_route_table_tags" {
  description = "Additional tags for the database route tables"
  type        = map(string)
  default     = {}
}

variable "redshift_route_table_tags" {
  description = "Additional tags for the redshift route tables"
  type        = map(string)
  default     = {}
}

variable "elasticache_route_table_tags" {
  description = "Additional tags for the elasticache route tables"
  type        = map(string)
  default     = {}
}

variable "intra_route_table_tags" {
  description = "Additional tags for the intra route tables"
  type        = map(string)
  default     = {}
}

variable "database_subnet_tags" {
  description = "Additional tags for the database subnets"
  type        = map(string)
  default     = {}
}

variable "database_subnet_group_tags" {
  description = "Additional tags for the database subnet group"
  type        = map(string)
  default     = {}
}

variable "redshift_subnet_tags" {
  description = "Additional tags for the redshift subnets"
  type        = map(string)
  default     = {}
}

variable "redshift_subnet_group_tags" {
  description = "Additional tags for the redshift subnet group"
  type        = map(string)
  default     = {}
}

variable "elasticache_subnet_tags" {
  description = "Additional tags for the elasticache subnets"
  type        = map(string)
  default     = {}
}

variable "intra_subnet_tags" {
  description = "Additional tags for the intra subnets"
  type        = map(string)
  default     = {}
}

variable "public_acl_tags" {
  description = "Additional tags for the public subnets network ACL"
  type        = map(string)
  default     = {}
}

variable "private_acl_tags" {
  description = "Additional tags for the private subnets network ACL"
  type        = map(string)
  default     = {}
}

variable "intra_acl_tags" {
  description = "Additional tags for the intra subnets network ACL"
  type        = map(string)
  default     = {}
}

variable "database_acl_tags" {
  description = "Additional tags for the database subnets network ACL"
  type        = map(string)
  default     = {}
}

variable "redshift_acl_tags" {
  description = "Additional tags for the redshift subnets network ACL"
  type        = map(string)
  default     = {}
}

variable "elasticache_acl_tags" {
  description = "Additional tags for the elasticache subnets network ACL"
  type        = map(string)
  default     = {}
}

variable "dhcp_options_tags" {
  description = "Additional tags for the DHCP option set (requires enable_dhcp_options set to true)"
  type        = map(string)
  default     = {}
}

variable "nat_gateway_tags" {
  description = "Additional tags for the NAT gateways"
  type        = map(string)
  default     = {}
}

variable "nat_eip_tags" {
  description = "Additional tags for the NAT EIP"
  type        = map(string)
  default     = {}
}

variable "vpn_gateway_tags" {
  description = "Additional tags for the VPN gateway"
  type        = map(string)
  default     = {}
}

variable "enable_dhcp_options" {
  description = "Should be true if you want to specify a DHCP options set with a custom domain name, DNS servers, NTP servers, netbios servers, and/or netbios server type"
  type        = bool
  default     = false
}

variable "dhcp_options_domain_name" {
  description = "Specifies DNS name for DHCP options set (requires enable_dhcp_options set to true)"
  type        = string
  default     = ""
}

variable "dhcp_options_domain_name_servers" {
  description = "Specify a list of DNS server addresses for DHCP options set, default to AWS provided (requires enable_dhcp_options set to true)"
  type        = list(string)
  default     = ["AmazonProvidedDNS"]
}

variable "dhcp_options_ntp_servers" {
  description = "Specify a list of NTP servers for DHCP options set (requires enable_dhcp_options set to true)"
  type        = list(string)
  default     = []
}

variable "dhcp_options_netbios_name_servers" {
  description = "Specify a list of netbios servers for DHCP options set (requires enable_dhcp_options set to true)"
  type        = list(string)
  default     = []
}

variable "dhcp_options_netbios_node_type" {
  description = "Specify netbios node_type for DHCP options set (requires enable_dhcp_options set to true)"
  type        = string
  default     = ""
}

variable "manage_default_vpc" {
  description = "Should be true to adopt and manage Default VPC"
  type        = bool
  default     = false
}

variable "default_vpc_name" {
  description = "Name to be used on the Default VPC"
  type        = string
  default     = ""
}

variable "default_vpc_enable_dns_support" {
  description = "Should be true to enable DNS support in the Default VPC"
  type        = bool
  default     = true
}

variable "default_vpc_enable_dns_hostnames" {
  description = "Should be true to enable DNS hostnames in the Default VPC"
  type        = bool
  default     = false
}

variable "default_vpc_enable_classiclink" {
  description = "Should be true to enable ClassicLink in the Default VPC"
  type        = bool
  default     = false
}

variable "default_vpc_tags" {
  description = "Additional tags for the Default VPC"
  type        = map(string)
  default     = {}
}

variable "manage_default_network_acl" {
  description = "Should be true to adopt and manage Default Network ACL"
  type        = bool
  default     = false
}

variable "default_network_acl_name" {
  description = "Name to be used on the Default Network ACL"
  type        = string
  default     = ""
}

variable "default_network_acl_tags" {
  description = "Additional tags for the Default Network ACL"
  type        = map(string)
  default     = {}
}

variable "public_dedicated_network_acl" {
  description = "Whether to use dedicated network ACL (not default) and custom rules for public subnets"
  type        = bool
  default     = false
}

variable "private_dedicated_network_acl" {
  description = "Whether to use dedicated network ACL (not default) and custom rules for private subnets"
  type        = bool
  default     = false
}

variable "intra_dedicated_network_acl" {
  description = "Whether to use dedicated network ACL (not default) and custom rules for intra subnets"
  type        = bool
  default     = false
}

variable "database_dedicated_network_acl" {
  description = "Whether to use dedicated network ACL (not default) and custom rules for database subnets"
  type        = bool
  default     = false
}

variable "redshift_dedicated_network_acl" {
  description = "Whether to use dedicated network ACL (not default) and custom rules for redshift subnets"
  type        = bool
  default     = false
}

variable "elasticache_dedicated_network_acl" {
  description = "Whether to use dedicated network ACL (not default) and custom rules for elasticache subnets"
  type        = bool
  default     = false
}

variable "default_network_acl_ingress" {
  description = "List of maps of ingress rules to set on the Default Network ACL"
  type        = list(map(string))

  default = [
    {
      rule_no    = 100
      action     = "allow"
      from_port  = 0
      to_port    = 0
      protocol   = "-1"
      cidr_block = "0.0.0.0/0"
    },
    {
      rule_no         = 101
      action          = "allow"
      from_port       = 0
      to_port         = 0
      protocol        = "-1"
      ipv6_cidr_block = "::/0"
    },
  ]
}

variable "default_network_acl_egress" {
  description = "List of maps of egress rules to set on the Default Network ACL"
  type        = list(map(string))

  default = [
    {
      rule_no    = 100
      action     = "allow"
      from_port  = 0
      to_port    = 0
      protocol   = "-1"
      cidr_block = "0.0.0.0/0"
    },
    {
      rule_no         = 101
      action          = "allow"
      from_port       = 0
      to_port         = 0
      protocol        = "-1"
      ipv6_cidr_block = "::/0"
    },
  ]
}

variable "public_inbound_acl_rules" {
  description = "Public subnets inbound network ACLs"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

variable "public_outbound_acl_rules" {
  description = "Public subnets outbound network ACLs"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

variable "private_inbound_acl_rules" {
  description = "Private subnets inbound network ACLs"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

variable "private_outbound_acl_rules" {
  description = "Private subnets outbound network ACLs"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

variable "intra_inbound_acl_rules" {
  description = "Intra subnets inbound network ACLs"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

variable "intra_outbound_acl_rules" {
  description = "Intra subnets outbound network ACLs"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

variable "database_inbound_acl_rules" {
  description = "Database subnets inbound network ACL rules"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

variable "database_outbound_acl_rules" {
  description = "Database subnets outbound network ACL rules"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

variable "redshift_inbound_acl_rules" {
  description = "Redshift subnets inbound network ACL rules"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

variable "redshift_outbound_acl_rules" {
  description = "Redshift subnets outbound network ACL rules"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

variable "elasticache_inbound_acl_rules" {
  description = "Elasticache subnets inbound network ACL rules"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

variable "elasticache_outbound_acl_rules" {
  description = "Elasticache subnets outbound network ACL rules"
  type        = list(map(string))

  default = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    },
  ]
}

