FROM base

RUN apt-get update \
 && apt-get install -y --no-install-recommends foo \
 && echo gooo

RUN apk update \
 && apk add --no-cache suuu looo

RUN apk --update add moo

RUN apk update --no-cache && apk upgrade --no-cache

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
  dpkg-reconfigure --frontend noninteractive locales && \
  update-locale LANG=en_US.UTF-8
