FROM base

LABEL foo="bar baz
USER  me

HEALTHCHECK CMD curl --fail http://localhost:3000 || exit 1
