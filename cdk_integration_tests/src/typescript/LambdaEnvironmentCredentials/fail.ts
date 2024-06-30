import {aws_lambda as lambda} from 'aws-cdk-lib';
import {aws_sam as sam} from 'aws-cdk-lib';

const cfnSecurityConfigurationProps1: lambda.FunctionProps = {
    name: 'name',
    role: "",
    environment: {
        "bla": "bla",
    }
};

const cfnSecurityConfigurationProps2: lambda.CfnFunctionProps = {
    name: 'name',
    role: "",
    environment: {
        variables: {
            "bla": "bla",
        }
    }
};

const cfnSecurityConfigurationProps3: sam.CfnFunctionProps = {
    name: 'name',
    environment: {
        variables: {
            bla: "bla",
        }
    }
};
