import {aws_lambda as lambda} from 'aws-cdk-lib';
import {aws_sam as sam} from 'aws-cdk-lib';

const cfnSecurityConfiguration1 = new lambda.Function(this, 'MyCfnSecurityConfiguration', {
    role: "",
    name: 'name',
    environment: {
        "bla": "bla",
    },
    environmentEncryption: {},
    "vpc": {},
});

const cfnSecurityConfiguration2 = new lambda.CfnFunction(this, 'MyCfnSecurityConfiguration', {
    role: "",
    name: 'name',
    environment: {
        variables: {
            "bla": "bla",
        }
    },
    kmsKeyArn: "arn",
    vpcConfig: {},
});

const cfnSecurityConfiguration3 = new sam.CfnFunction(this, 'MyCfnSecurityConfiguration', {
    role: "",
    name: 'name',
    environment: {
        variables: {
            bla: "bla",
        }
    },
    kmsKeyArn: "arn",
    vpcConfig: {},
});

const cfnSecurityConfigurationProps1: lambda.FunctionProps = {
    name: 'name',
    role: "",
    environment: {
        "bla": "bla",
    },
    environmentEncryption: {},
    reservedConcurrentExecutions: 1,
};

const cfnSecurityConfigurationProps2: lambda.CfnFunctionProps = {
    name: 'name',
    role: "",
    environment: {
        variables: {
            "bla": "bla",
        }
    },
    kmsKeyArn: "arn",
    reservedConcurrentExecutions: 1,
};

const cfnSecurityConfigurationProps3: sam.CfnFunctionProps = {
    name: 'name',
    environment: {
        variables: {
            bla: "bla",
        }
    },
    kmsKeyArn: "arn",
    reservedConcurrentExecutions: 1,
};
