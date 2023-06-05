#checkov:skip=CKV_DOCKER_5: no need to skip
#checkov:skip=CKV2_DOCKER_7: no need to skip graph check
FROM gliderlabs/alpine:3.3
RUN apk --no-cache add nginx
EXPOSE 3000 80 443 22
#checkov:skip=CKV_DOCKER_1: required
CMD ["nginx", "-g", "daemon off;"]