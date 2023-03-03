FROM alpine:3.5
RUN curl https://example.com
RUN curl --fake https://example.com
RUN curl -lol https://example.com
RUN curl https://example.com | grep -k lol
RUN curl https://example.com; grep /etc/passwd -k lol
RUN curl https://example.com &&\
    grep /etc/passwd -k lol
RUN curl https://example.com ||\
    grep /etc/passwd -k lol
