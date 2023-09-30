FROM debian:bullseye
RUN apt-get install python3
RUN apt-get install python3 | grep "--allow-unauthenticated"
RUN apt-get update && apt-get install \
    python3
RUN apt-get update &&\
    echo "--allow-unauthenticated"
