---
layout: default
published: true
title: Dockerfile configuration scanning
nav_order: 20
---

# Dockerfile configuration scanning
Checkov supports the evaluation of policies on your Dockerfile files.
When using checkov to scan a directory that contains Dockerfile it will validate if the file is compliant with Docker best practices such as not using root user, making sure health check exists and not exposing SSH port.  

Full list of Dockerfile policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/dockerfile.html).


### Example misconfigured Dockerfile

```dockerfile
FROM node:alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000 22
HEALTHCHECK CMD curl --fail http://localhost:3000 || exit 1
CMD ["node","app.js"]
```
### Running in CLI

```bash
checkov -d . --framework dockerfile
```

### Example output

```bash
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: x.x.x 

dockerfile scan results:

Passed checks: 3, Failed checks: 2, Skipped checks: 0

Check: CKV_DOCKER_5: "Ensure update instructions are not use alone in the Dockerfile"
	PASSED for resource: /Dockerfile.
	File: /Dockerfile:1-8
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/docker-policies/docker-policy-index/ensure-update-instructions-are-not-used-alone-in-the-dockerfile

Check: CKV_DOCKER_7: "Ensure the base image uses a non latest version tag"
	PASSED for resource: /Dockerfile.
	File: /Dockerfile:1-8
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/docker-policies/ensure-the-base-image-uses-a-non-latest-version-tag

Check: CKV_DOCKER_2: "Ensure that HEALTHCHECK instructions have been added to container images"
	PASSED for resource: /Dockerfile.HEALTHCHECK
	File: /Dockerfile:7-7
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/docker-policies/ensure-that-healthcheck-instructions-have-been-added-to-container-images

Check: CKV_DOCKER_1: "Ensure port 22 is not exposed"
	FAILED for resource: /Dockerfile.EXPOSE
	File: /Dockerfile:6-6
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/docker-policies/ensure-port-22-is-not-exposed

		6 | EXPOSE 3000 22


Check: CKV_DOCKER_3: "Ensure that a user for the container has been created"
	FAILED for resource: /Dockerfile.
	File: /Dockerfile:1-8
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/docker-policies/ensure-that-a-user-for-the-container-has-been-created

		1 | FROM node:alpine
		2 | WORKDIR /usr/src/app
		3 | COPY package*.json ./
		4 | RUN npm install
		5 | COPY . .
		6 | EXPOSE 3000 22
		7 | HEALTHCHECK CMD curl --fail http://localhost:3000 || exit 1
		8 | CMD ["node","app.js"]
```

