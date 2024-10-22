FROM --platform=linux/amd64 node:16 as FOO
RUN npm install

FROM --platform=linux/amd64 node:16 as BAR
RUN npm run

USER nobody
HEALTHCHECK CMD curl --fail http://localhost:3000 || exit 1

CMD mycommand.sh
