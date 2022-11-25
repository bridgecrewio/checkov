#!/bin/bash

##### Things to change #####
set -e
CONTAINER_DEV_IMAGE="$CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG"
echo "Container Dev Image: $CONTAINER_DEV_IMAGE"
echo "Container Commit Slug: $CI_COMMIT_REF_SLUG"

docker build \
  ${DOCKER_LABELS} \
  --no-cache \
  --tag ${CONTAINER_DEV_IMAGE} \
  --file Dockerfile .

docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
docker push ${CONTAINER_DEV_IMAGE}


