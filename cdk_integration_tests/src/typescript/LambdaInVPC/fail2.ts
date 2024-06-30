import { aws_lambda as lambda } from 'aws-cdk-lib';
import { aws_sam as sam } from 'aws-cdk-lib';

const cfnSecurityConfiguration1 = new lambda.Function(this, 'MyCfnSecurityConfiguration', {
    role: "",
    name: 'name',
});

const cfnSecurityConfiguration2 = new lambda.CfnFunction(this, 'MyCfnSecurityConfiguration', {
    role: "",
    name: 'name',
    environment: {
        variables: {
            "bla": "bla",
        }
    }
});

const cfnSecurityConfiguration3 = new sam.CfnFunction(this, 'MyCfnSecurityConfiguration', {
    role: "",
    name: 'name',
    environment: {
        variables: {
            bla: "bla",
        }
    }
});
