FROM alpine:3 AS base
COPY test.sh /test.sh

FROM base AS build
LABEL maintainer=checkov

FROM base
