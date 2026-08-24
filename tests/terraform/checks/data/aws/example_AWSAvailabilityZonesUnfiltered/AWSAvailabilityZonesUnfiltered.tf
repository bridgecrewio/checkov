## SHOULD FAIL: no constraining argument at all; silently expands when a new AZ is added
data "aws_availability_zones" "unfiltered" {}

## SHOULD FAIL: `state` constrains zone health, not identity; a newly-added healthy AZ still appears
data "aws_availability_zones" "state_only" {
  state = "available"
}

## SHOULD FAIL: filter on opt-in-status constrains a zone attribute, not identity
data "aws_availability_zones" "filter_opt_in_status" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

## SHOULD PASS: constrained via exclude_names (pins identity)
data "aws_availability_zones" "excluded_by_name" {
  exclude_names = ["us-east-1e"]
}

## SHOULD PASS: constrained via exclude_zone_ids (pins identity)
data "aws_availability_zones" "excluded_by_id" {
  exclude_zone_ids = ["use1-az3"]
}

## SHOULD PASS: constrained via an identity-based filter (zone-name)
data "aws_availability_zones" "filtered_by_name" {
  filter {
    name   = "zone-name"
    values = ["us-east-1a", "us-east-1b", "us-east-1c"]
  }
}

## SHOULD PASS: constrained via an identity-based filter (zone-id)
data "aws_availability_zones" "filtered_by_id" {
  filter {
    name   = "zone-id"
    values = ["use1-az1", "use1-az2"]
  }
}
