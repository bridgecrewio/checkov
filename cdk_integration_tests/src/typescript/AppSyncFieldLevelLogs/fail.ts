// Import necessary AWS CDK packages
import * as appsync from '@aws-cdk/aws-appsync';

// Example of a log configuration that does not enable field-level logging
// FINDING
const logConfig: appsync.LogConfig = {
  // log configuration details
};

// This should match the pattern and be flagged as a vulnerability
// SINK
const graphqlApiWithoutLogs = new appsync.GraphqlApi(this, 'apiWithoutLogs', {
  // other configuration details
  logConfig: {
    // Incorrect or missing fieldLogLevel configuration
  }
});

// The SAST engine should flag 1 vulnerability: `graphqlApiWithoutLogs`.
