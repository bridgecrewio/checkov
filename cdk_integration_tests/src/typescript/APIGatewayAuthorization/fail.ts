// Import necessary AWS CDK packages
import * as apigateway from '@aws-cdk/aws-apigateway';
import { Resource } from '@aws-cdk/core';

// Example resource and method declarations
const resource: Resource = new Resource(); // Placeholder for actual resource initialization

// Test cases for the policy patterns

// This should match the first pattern and not be sanitized by the second pattern
// SOURCE
const method1 = resource.addMethod('GET', new apigateway.MockIntegration(), {
  apiKeyRequired: false
});

// This should match the second pattern
// SINK
const method2 = resource.addMethod('POST', new apigateway.MockIntegration(), {
  authorizationType: apigateway.AuthorizationType.NONE
});

// The SAST engine should flag 2 vulnerabilities: `method1` and `method2`.
