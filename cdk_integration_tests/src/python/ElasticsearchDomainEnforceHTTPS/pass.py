from aws_cdk import aws_elasticsearch as elasticsearch

# access_policies: Any

cfn_domain = elasticsearch.CfnDomain(self, "MyCfnDomain",
    access_policies=access_policies,
    advanced_options={
        "advanced_options_key": "advancedOptions"
    },
    advanced_security_options=elasticsearch.CfnDomain.AdvancedSecurityOptionsInputProperty(
        anonymous_auth_enabled=False,
        enabled=False,
        internal_user_database_enabled=False,
        master_user_options=elasticsearch.CfnDomain.MasterUserOptionsProperty(
            master_user_arn="masterUserArn",
            master_user_name="masterUserName",
            master_user_password="masterUserPassword"
        )
    ),
    cognito_options=elasticsearch.CfnDomain.CognitoOptionsProperty(
        enabled=False,
        identity_pool_id="identityPoolId",
        role_arn="roleArn",
        user_pool_id="userPoolId"
    ),
    domain_arn="domainArn",
    domain_endpoint_options=elasticsearch.CfnDomain.DomainEndpointOptionsProperty(
        custom_endpoint="customEndpoint",
        custom_endpoint_certificate_arn="customEndpointCertificateArn",
        custom_endpoint_enabled=False,
        enforce_https=True,
        tls_security_policy="tlsSecurityPolicy"
    ),
    domain_name="domainName",
    ebs_options=elasticsearch.CfnDomain.EBSOptionsProperty(
        ebs_enabled=False,
        iops=123,
        volume_size=123,
        volume_type="volumeType"
    ),
    elasticsearch_cluster_config=elasticsearch.CfnDomain.ElasticsearchClusterConfigProperty(
        cold_storage_options=elasticsearch.CfnDomain.ColdStorageOptionsProperty(
            enabled=False
        ),
        dedicated_master_count=123,
        dedicated_master_enabled=False,
        dedicated_master_type="dedicatedMasterType",
        instance_count=123,
        instance_type="instanceType",
        warm_count=123,
        warm_enabled=False,
        warm_type="warmType",
        zone_awareness_config=elasticsearch.CfnDomain.ZoneAwarenessConfigProperty(
            availability_zone_count=123
        ),
        zone_awareness_enabled=False
    ),
    elasticsearch_version="elasticsearchVersion",
    encryption_at_rest_options=elasticsearch.CfnDomain.EncryptionAtRestOptionsProperty(
        enabled=False,
        kms_key_id="kmsKeyId"
    ),
)