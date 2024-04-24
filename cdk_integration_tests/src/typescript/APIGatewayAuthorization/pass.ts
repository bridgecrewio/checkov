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
