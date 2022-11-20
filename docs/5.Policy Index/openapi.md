---
layout: default
title: openapi resource scans
nav_order: 1
---

# openapi resource scans (auto generated)

|    |               | Id       | Type                | Entity                                                                                                                                       | Policy   | IaC                                                         |
|----|---------------|----------|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------|----------|-------------------------------------------------------------|
|  0 | CKV_OPENAPI_1 | resource | securityDefinitions | Ensure that securityDefinitions is defined and not empty - version 2.0 files                                                                 | OpenAPI  | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  1 | CKV_OPENAPI_2 | resource | security            | Ensure that if the security scheme is not of type 'oauth2', the array value must be empty - version 2.0 files                                | OpenAPI  | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  2 | CKV_OPENAPI_3 | resource | components          | Ensure that security schemes don't allow cleartext credentials over unencrypted channel - version 3.x.y files                                | OpenAPI  | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  3 | CKV_OPENAPI_4 | resource | security            | Ensure that the global security field has rules defined                                                                                      | OpenAPI  | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  4 | CKV_OPENAPI_5 | resource | security            | Ensure that security operations is not empty.                                                                                                | OpenAPI  | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  5 | CKV_OPENAPI_6 | resource | security            | Ensure that security requirement defined in securityDefinitions - version 2.0 files                                                          | OpenAPI  | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  6 | CKV_OPENAPI_7 | resource | security            | Ensure that the path scheme does not support unencrypted HTTP connection where all transmissions are open to interception- version 2.0 files | OpenAPI  | https://github.com/bridgecrewio/checkov/tree/master/checkov |


---


