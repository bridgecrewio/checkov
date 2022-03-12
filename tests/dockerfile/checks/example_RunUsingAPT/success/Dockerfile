FROM busybox:1.0
RUN apt-get install curl
HEALTHCHECK CMD curl --fail http://localhost:3000 || exit 1