FROM ubuntu
RUN mkdir /app
RUN groupadd -r tronxd && useradd -r -s /bin/false -g tronxd tronxd
WORKDIR /app
COPY . /app
RUN chown -R tronxd:tronxd /app
USER tronxd
CMD node index.js
