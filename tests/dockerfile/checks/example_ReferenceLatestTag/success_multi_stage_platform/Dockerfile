FROM --platform=$BUILDPLATFORM python:3.11-slim AS build
COPY test.sh /test.sh

FROM build as run
LABEL maintainer=checkov
