import { aws_glue as glue } from 'aws-cdk-lib';

const cfnSecurityConfiguration1 = new glue.CfnCrawler(this, 'MyCfnSecurityConfiguration', {
  name: 'name',
});

const cfnSecurityConfiguration2 = new glue.CfnDevEndpoint(this, 'MyCfnSecurityConfiguration', {
  name: 'name',
});

const cfnSecurityConfiguration3 = new glue.CfnJob(this, 'MyCfnSecurityConfiguration', {
  name: 'name',
});
