// Import necessary AWS CDK packages
import * as appsync from '@aws-cdk/aws-appsync';

// Example of a log configuration that does not enable field-level logging
// FINDING
const logConfig: appsync.LogConfig = {
  // log configuration details
};

// This should not match the pattern as it includes a logConfig with FieldLogLevel
const graphqlApiWithLogs = new appsync.GraphqlApi(this, 'apiWithLogs', {
  // other configuration details
  logConfig: {
    fieldLogLevel: appsync.FieldLogLevel.ALL // This is the correct configuration
  }
});
