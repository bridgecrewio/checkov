---
layout: default
published: true
title: OpenAPI configuration scanning
nav_order: 20
---

# OpenAPI configuration scanning
Checkov supports the evaluation of policies on your OpenAPI files.
When using checkov to scan a directory that contains OpenAPI manifests it will validate if the file is compliant with OpenAPI best practices such as securityDefinitions and security requirement are well-defined, and more.  

Full list of OpenAPI policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/openapi.html).

### Example misconfigured OpenAPI

```yaml
{
  "swagger": "2.0",
  "info": {
    "title": "example",
    "version": "1.0.0"
  },
  "paths": {
    "/": {
      "get": {
        "operationId": "example",
        "summary": "example",
        "responses": {
          "200": {
            "description": "200 response"
          }
        },
        "parameters": [
          {
            "name": "limit2",
            "in": "body",
            "required": true,
            "schema": {
              "type": "object"
            }
          }
        ],
        "security": [
          {
            "api_key": []
          }
        ]
      }
    }
  },
  "securityDefinitions": {
    "petstore_auth": {
      "type": "oauth2",
      "authorizationUrl": "http://swagger.io/api/oauth/dialog",
      "flow": "implicit",
      "scopes": {
        "write:pets": "write",
        "read:pets": "read"
      }
    }
  }
}

```
### Running in CLI

```bash
checkov -d . --framework openapi
```

### Example output
```bash
 
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: x.x.x 


openapi scan results:

Passed checks: 4, Failed checks: 2, Skipped checks: 0

Check: CKV_OPENAPI_2: "Ensure that if the security scheme is not of type 'oauth2', the array value must be empty"
	PASSED for resource: security
	File: /openapi.yaml:2-47
Check: CKV_OPENAPI_5: "Ensure that security operations is not empty."
	PASSED for resource: security
	File: /openapi.yaml:2-47
Check: CKV_OPENAPI_1: "Ensure that securityDefinitions is defined and not empty."
	PASSED for resource: securityDefinitions
	File: /../aya/openapi.yaml:36-46
Check: CKV_OPENAPI_3: "Ensure that security schemes don't allow cleartext credentials over unencrypted channel"
	PASSED for resource: components
	File: /openapi.yaml:2-47
Check: CKV_OPENAPI_6: "Ensure that security requirement defined in securityDefinitions."
	FAILED for resource: security
	File: /openapi.yaml:27-31

		27 |         "security": [
		28 |           {
		29 |             "api_key": []
		30 |           }
		31 |         ]
		
Check: CKV_OPENAPI_4: "Ensure that the global security field has rules defined"
	FAILED for resource: security
	File: /openapi.yaml:1-47

		1  | {
		2  |   "swagger": "2.0",
		3  |   "info": {
		4  |     "title": "example",
		5  |     "version": "1.0.0"
		6  |   },
		7  |   "paths": {
		8  |     "/": {
		9  |       "get": {
		10 |         "operationId": "example",
		11 |         "summary": "example",
		12 |         "responses": {
		13 |           "200": {
		14 |             "description": "200 response"
		15 |           }
		16 |         },
		17 |         "parameters": [
		18 |           {
		19 |             "name": "limit2",
		20 |             "in": "body",
		21 |             "required": true,
		22 |             "schema": {
		23 |               "type": "object"
		24 |             }
		25 |           }
		26 |         ],
		27 |         "security": [
		28 |           {
		29 |             "api_key": []
		30 |           }
		31 |         ]
		32 |       }
		33 |     }
		34 |   },
		35 |   "securityDefinitions": {
		36 |     "petstore_auth": {
		37 |       "type": "oauth2",
		38 |       "authorizationUrl": "http://swagger.io/api/oauth/dialog",
		39 |       "flow": "implicit",
		40 |       "scopes": {
		41 |         "write:pets": "write",
		42 |         "read:pets": "read"
		43 |       }
		44 |     }
		45 |   }
		46 | }


```
