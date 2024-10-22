FROM alpine:3.5
RUN wget https://example.com
RUN wget --no-progress -o file https://example.com
RUN wget -lol https://example.com
RUN wget https://example.com | grep "--no-check-certificate" /etc/passwd
RUN wget https://example.com; grep "--no-check-certificate" /etc/passwd
RUN wget https://example.com &&\
    echo "--no-check-certificate"
RUN wget https://example.com ||\
    grep "--no-check-certificate" /etc/passwd
