// Import necessary AWS CDK packages
import * as apigateway from '@aws-cdk/aws-apigateway';
import { Resource } from '@aws-cdk/core';

// Example resource and method declarations
const resource: Resource = new Resource(); // Placeholder for actual resource initialization

// Test cases for the policy patterns

// This should not match any pattern as it includes an authorization type
// SANITIZER
const method3 = resource.addMethod('PUT', new apigateway.MockIntegration(), {
  authorizationType: apigateway.AuthorizationType.COGNITO,
  apiKeyRequired: true
});

// This should not match any pattern as it includes an authorization type and is not open
const method4 = resource.addMethod('DELETE', new apigateway.MockIntegration(), {
  authorizationType: apigateway.AuthorizationType.IAM
});

// The SAST engine should flag 2 vulnerabilities: `method1` and `method2`.
