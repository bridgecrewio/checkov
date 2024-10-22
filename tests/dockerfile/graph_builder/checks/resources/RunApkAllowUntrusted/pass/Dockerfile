FROM alpine:3.5
RUN apk add a-car
RUN apk add a-handbag | grep "--allow-untrusted"
RUN apk upgrade --no-cache && apk add \
    a-mobile-phone a-dvd
RUN apk upgrade &&\
    echo "--allow-untrusted"
