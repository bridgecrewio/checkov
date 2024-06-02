// Import necessary AWS CDK packages
import * as appsync from '@aws-cdk/aws-appsync';

// Example of a log configuration
// FINDING
const logConfig: appsync.LogConfig = {
  // log configuration details
};

// This should match the pattern and be flagged as a vulnerability
// SINK
const graphqlApiWithoutRole = new appsync.GraphqlApi(this, 'apiWithoutRole', {
  // other configuration details
  logConfig: {
    // log configuration details without role
  }
});

// The SAST engine should flag 1 vulnerability: `graphqlApiWithoutRole`.
