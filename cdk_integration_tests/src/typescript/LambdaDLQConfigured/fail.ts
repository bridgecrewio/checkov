import { aws_lambda as lambda } from 'aws-cdk-lib';
import { aws_sam as sam } from 'aws-cdk-lib';

const cfnSecurityConfigurationProps1: lambda.FunctionProps = {
  name: 'name',
  role: "",
};

const cfnSecurityConfigurationProps1: lambda.CfnFunctionProps = {
  name: 'name',
  role: "",
};

const cfnSecurityConfigurationProps2: sam.CfnFunctionProps = {
  name: 'name',
};
