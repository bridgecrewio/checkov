expected_postgres_module = {"create": True,
                            "name": "${var.name}",
                            "use_name_prefix": True,
                            "description": "Security Group managed by Terraform",
                            "vpc_id": "${var.vpc_id}",
                            "revoke_rules_on_delete": False,
                            "tags": {},
                            "ingress_rules": ["postgresql-tcp"],
                            "ingress_with_self": [{"rule": "all-all"}],
                            "number_of_computed_egress_rules": 0,
                            }

expected_terragoat_local_resource_prefix = {'resource_prefix': {'value': 'test_id-acme-dev'}}

expected_terragoat_db_instance = {'name': 'db1',
                                  'engine': 'mysql',
                                  'option_group_name': 'og-test_id-acme-dev',
                                  'parameter_group_name': 'pg-test_id-acme-dev',
                                  'db_subnet_group_name': 'sg-test_id-acme-dev',
                                  'vpc_security_group_ids': ['aws_security_group.default.id'],
                                  'identifier': 'rds-test_id-acme-dev',
                                  'password': 'Aa1234321Bb',
                                  'tags': {'Name': 'test_id-acme-dev-rds',
                                            'Environment': 'test_id-acme-dev'}
                                  }


expected_eks = {
    "resource": {
        "aws_eks_cluster.tf_eks": {
            "version": ["1.19"],
            "vpc_config": {
                "security_group_ids": ["aws_security_group.master.id"],
                "subnet_ids": "aws_subnet.eks[*].id"
            },
        }
    }
}


expected_provider = {
    "provider": {
        "aws": {
            "access_key": ["AKIAVAN"],
            "secret_key": ["0CU4jk0"],
            "region": ["us-west-2"],
        }
    }
}
