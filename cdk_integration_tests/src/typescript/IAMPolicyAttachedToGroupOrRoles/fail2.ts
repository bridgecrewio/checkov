import { aws_iam as iam } from 'aws-cdk-lib';

const a = new iam.Policy(this, 'userpool-policy', {
  statements: [new iam.PolicyStatement({
    actions: ['cognito-idp:DescribeUserPool'],
    resources: ['Arn'],
  })],
  users: ['sdsd']
});

const b = new iam.Policy(this, 'userpool-policy', {
  statements: [new iam.PolicyStatement({
    actions: ['cognito-idp:DescribeUserPool'],
    resources: ['Arn'],
  })],
});
console.log('dsd')
b.attachToUser({})

const c = new iam.Policy(this, 'userpool-policy', {
  statements: [new iam.PolicyStatement({
    actions: ['cognito-idp:DescribeUserPool'],
    resources: ['Arn'],
  })],
});
c.attachToUser({})