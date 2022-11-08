#!/bin/bash

##### Things to change #####
VERSION="v20221108.0219"
set -e

CONTAINER_VERSION="$CI_REGISTRY_IMAGE:${VERSION}"
CONTAINER_RELEASE_IMAGE="$CI_REGISTRY_IMAGE:latest"
echo "Container Version: $CONTAINER_VERSION"
echo "Container Release Image: $CONTAINER_RELEASE_IMAGE"
echo "Container Commit Slug: $CI_COMMIT_REF_SLUG"

docker build \
  ${DOCKER_LABELS} \
  --no-cache \
  --tag ${CONTAINER_VERSION} \
  --tag ${CONTAINER_RELEASE_IMAGE} \
  --file Dockerfile .

echo ${CONTAINER_TEST_IMAGE}
echo ${CONTAINER_VERSION}
echo ${CONTAINER_RELEASE_IMAGE}

docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
docker push ${CONTAINER_VERSION}
docker push ${CONTAINER_RELEASE_IMAGE}

