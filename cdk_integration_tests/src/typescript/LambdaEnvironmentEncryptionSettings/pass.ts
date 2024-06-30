import {aws_lambda as lambda} from 'aws-cdk-lib';
import {aws_sam as sam} from 'aws-cdk-lib';

const cfnSecurityConfiguration1 = new lambda.Function(this, 'MyCfnSecurityConfiguration', {
    role: "",
    name: 'name',
});

const cfnSecurityConfiguration2 = new lambda.CfnFunction(this, 'MyCfnSecurityConfiguration', {
    role: "",
    name: 'name',
});

const cfnSecurityConfiguration3 = new sam.CfnFunction(this, 'MyCfnSecurityConfiguration', {
    role: "",
    name: 'name',
});

const cfnSecurityConfigurationProps1: lambda.FunctionProps = {
    name: 'name',
    role: "",
};

const cfnSecurityConfigurationProps2: lambda.CfnFunctionProps = {
    name: 'name',
    role: "",
};

const cfnSecurityConfigurationProps3: sam.CfnFunctionProps = {
    name: 'name',
};
