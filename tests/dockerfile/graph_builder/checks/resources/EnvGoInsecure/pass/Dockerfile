FROM golang:1.14
ENV ASDFGOINSECURE=example.com
ENV ASDFGOINSECURE example.com
ARG GOINSECUREASDF=example.com
ARG GOINSECUREASDF example.com
ARG GOINSECUREASDF example.com
ENV TEST=YES ASDFGOINSECURE=0
ENV ASDFGOINSECURE=0 FAIL=FALSE
ENV PASS=TRUE GOINSECUREASDF=example.com

RUN go build
RUN go mod download
RUN ASDFGOINSECURE=example.com go mod download
RUN ASDFGOINSECURE="example.com" go mod download
RUN ASDFGOINSECURE='example.com' go mod download
RUN GOINSECUREASDF=example.com \
    ASDFGOINSECURE=example.com go mod download
