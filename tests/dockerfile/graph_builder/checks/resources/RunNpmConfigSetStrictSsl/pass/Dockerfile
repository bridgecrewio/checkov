FROM node:18
RUN npm config set strict-ssl=true
RUN yarn config set "strict-ssl"=true
RUN npm config set 'strict-ssl'=true

RUN npm config set strict-ssl true
RUN yarn config set "strict-ssl" true
RUN npm config set 'strict-ssl' true

RUN yarn      config     set      strict-ssl     true
RUN npm      config     set     "strict-ssl"    true
RUN yarn      config     set     'strict-ssl'    true

RUN npm set strict-ssl true
RUN yarn set "strict-ssl" true
RUN npm set 'strict-ssl' true

RUN yarn      set      strict-ssl     true
RUN npm      set     "strict-ssl"    true
RUN yarn      set     'strict-ssl'    true

RUN npm config set audit false
RUN yarn config set audit false

RUN npm set audit false
RUN yarn set audit false

RUN npm config set strict-ssl true || false
RUN yarn config set strict-ssl true || false

RUN npm config get strict-ssl || false
RUN yarn config get strict-ssl || false

RUN npm install strict-ssl false
RUN yarn install strict-ssl false

RUN true && npm install strict-ssl true || false
RUN echo false | yarn install strict-ssl true > out.txt

RUN npm  \
    set   \
    strict-ssl  \
    true && gcc -Wpedantic less.c