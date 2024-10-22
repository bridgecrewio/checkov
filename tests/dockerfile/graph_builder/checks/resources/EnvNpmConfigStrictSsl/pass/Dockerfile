FROM node:18
ENV NPM_CONFIG_STRICT_SSL=true
ENV NPM_CONFIG_STRICT_SSL true
ENV NPM_CONFIG_STRICT_SSL Nyota_Uhura
ARG NPM_CONFIG_STRICT_SSL=true
ARG NPM_CONFIG_STRICT_SSL true
ARG NPM_CONFIG_STRICT_SSL James_Tiberius_Kirk
ENV LOL=123 ASDFNPM_CONFIG_STRICT_SSL=false
ENV ASDFNPM_CONFIG_STRICT_SSL=false LOL=321
ENV LOL=123 \
    ASDFNPM_CONFIG_STRICT_SSL="false"
ENV LOL=321 NPM_CONFIG_STRICT_SSL=true
ENV NPM_CONFIG_STRICT_SSL      "true"
ARG NPM_CONFIG_STRICT_SSLLOL=false

ENV npm_config_strict_ssl=true
ENV npm_config_strict_ssl true
ENV npm_config_strict_ssl Nyota_Uhura
ARG npm_config_strict_ssl=true
ARG npm_config_strict_ssl true
ARG npm_config_strict_ssl James_Tiberius_Kirk
ENV LOL=123 asdfnpm_config_strict_ssl=false
ENV asdfnpm_config_strict_ssl=false LOL=321
ENV LOL=123 \
    asdfnpm_config_strict_ssl="false"
ENV LOL=321 npm_config_strict_ssl=true
ENV npm_config_strict_ssl      "true"
ARG npm_config_strict_ssllol=false

RUN npm install
RUN NPM_CONFIG_STRICT_SSL=true npm install
RUN NPM_CONFIG_STRICT_SSL="true" npm install
RUN NPM_CONFIG_STRICT_SSL='true' npm install
RUN NPM_CONFIG_STRICT_SSL="false\"" npm install
RUN NPM_CONFIG_STRICT_SSL='false\'' npm install
RUN LOL=Spok \
    ASDFNPM_CONFIG_STRICT_SSL="false" npm install
RUN LOL=123 NPM_CONFIG_STRICT_SSL=true npm install
RUN NPM_CONFIG_STRICT_SSLLOL=false npm install

RUN npm_config_strict_ssl=true npm install
RUN npm_config_strict_ssl="true" npm install
RUN npm_config_strict_ssl='true' npm install
RUN npm_config_strict_ssl="false\"" npm install
RUN npm_config_strict_ssl='false\'' npm install
RUN LOL=Spok \
    asdfnpm_config_strict_ssl="false" npm install
RUN LOL=123 npm_config_strict_ssl=true npm install
RUN npm_config_strict_ssllol=false npm install
