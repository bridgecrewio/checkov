import { aws_iam as iam } from 'aws-cdk-lib';

const a = new iam.Policy(this, 'userpool-policy', {
  statements: [new iam.PolicyStatement({
    actions: ['cognito-idp:DescribeUserPool'],
    resources: ['Arn'],
  })],
});

const cfnSecurityConfigurationProps1: iam.PolicyProps = {
  statements: [new iam.PolicyStatement({
    actions: ['cognito-idp:DescribeUserPool'],
    resources: ['Arn'],
  })],
};
